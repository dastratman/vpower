import sys
import time

import platform

from ant.core import driver, node
from ant.core.constants import *

from usb.core import find

from constants import *

from CadenceListener import CadenceListener
from sensors.PowerMeterTx import PowerMeterTx
from sensors.SpeedSensorTx import SpeedSensorTx
from sensors.SpeedCadenceSensorRx import SpeedCadenceSensorRx
from config import DEBUG, LOG, NETKEY, POWER_CALCULATOR, POWER_SENSOR_ID, SENSOR_TYPE, SENSOR_ID, SENSOR_CHANNEL, SPEED_SENSOR_ID

class AntDevice():
    def __init__(self):
        self.antnode = None
        self.sensor = None
        self.power_meter = None
        self.speed_sensor = None
        self.cadence_listener = None
        self.pywin32 = False

        if platform.system() == 'Windows':
            def on_exit(sig, func=None):
                self.stop_ant()
            try:
                import win32api
                win32api.SetConsoleCtrlHandler(on_exit, True)
                self.pywin32 = True
            except ImportError:
                print("Warning: pywin32 is not installed, use Ctrl+C to stop")

    def stop_ant(self):
        if self.sensor:
            print("Closing sensor")
            self.sensor.close()
            self.sensor.unassign()
        if self.power_meter:
            print("Closing power meter")
            self.power_meter.close()
            self.power_meter.unassign()
        if self.antnode:
            print("Stopping ANT node")
            self.antnode.stop()

    def start_ant(self):
        print("Using " + POWER_CALCULATOR.__class__.__name__)

        devs = find(find_all=True, idVendor=0x0fcf)
        for dev in devs:
            if dev.idProduct in [0x1008, 0x1009]:
                print("=====================")
                print("ANT+ device found")
                print("Device idVendor: " + str(dev.idVendor))
                print("Device idProduct: " + str(dev.idProduct))
                print("Device bus: " + str(dev.bus))
                print("Device address: " + str(dev.address))
                print("=====================")

                stick = driver.USB2Driver(log=LOG, debug=DEBUG, idProduct=dev.idProduct, bus=dev.bus, address=dev.address)
                try:
                    stick.open()
                except:
                    continue
                stick.close()
                break
        else:
            print("No ANT devices available")
            if getattr(sys, 'frozen', False):
                input()
            sys.exit()

        self.antnode = node.Node(stick)

        print("Starting ANT node")
        self.antnode.start()


    def start_sensor(self):
        print("Starting sensor")
        try:
            # Create the sensor object and open it          

            if SENSOR_TYPE == SPEED_DEVICE_TYPE:
                self.sensor = SpeedCadenceSensorRx(self.antnode, SENSOR_TYPE, SENSOR_ID & 0xffff, SENSOR_CHANNEL)
            elif SENSOR_TYPE == CADENCE_DEVICE_TYPE:
                network = node.Network(NETKEY, 'N:ANT+')
                self.antnode.setNetworkKey(0, network)
                self.sensor = self.antnode.getFreeChannel()
                self.sensor.assign(network, CHANNEL_TYPE_TWOWAY_RECEIVE)
                self.sensor.setID(122, 0, 0)
                self.sensor.searchTimeout = TIMEOUT_NEVER
                self.sensor.period = 8102
                self.sensor.frequency = 57

            print("Opening sensor")
            self.sensor.open()
        except Exception as e:
            print("sensor error: " + repr(e))
            self.sensor = None

    def start_power_meter(self):
        print("Starting power meter with ANT+ ID " + repr(POWER_SENSOR_ID))
        try:
            # Create the power meter object and open it
            self.power_meter = PowerMeterTx(self.antnode, POWER_SENSOR_ID)
            self.power_meter.open()
        except Exception as e:
            print("power_meter error: " + repr(e))
            self.power_meter = None

    def start_speed_sensor(self):
        print("Starting speed sensor with ANT+ ID " + repr(SPEED_SENSOR_ID))
        try:
            # Create the power meter object and open it
            self.speed_sensor = SpeedSensorTx(self.antnode, SPEED_SENSOR_ID)
            self.speed_sensor.open()
        except Exception as e:
            print("speed_sensor error: " + repr(e))
            self.speed_sensor = None

    def register_callbacks(self):
        print("Registering callbacks")

        if SENSOR_TYPE == SPEED_DEVICE_TYPE:
            # Notify the power calculator every time we get a speed event
            self.sensor.notify_change(POWER_CALCULATOR)
        elif SENSOR_TYPE == CADENCE_DEVICE_TYPE:
            self.cadence_listener = CadenceListener(self.power_meter, self.speed_sensor)
            self.cadence_listener.load_power_curve()
            self.antnode.registerEventListener(self.cadence_listener)

    def wait_loop(self):
        print("Main wait loop")

        last_speed = 0
        last_event = 0
        last_time = 0
        stopped = True

        while True:
            try:
                # Workaround for RGT Cycling and GTBikeV
                if not stopped:
                    t = int(time.time())
                    if t >= last_time + 3:

                        # Speed
                        if SENSOR_TYPE == SPEED_DEVICE_TYPE:
                            if self.sensor.currentData.speedEventTime == last_speed:
                                # Set power to zero if speed sensor doesn't update for 3 seconds
                                self.power_meter.powerData.instantaneousPower = 0
                                stopped = True
                            last_speed = self.sensor.currentData.speedEventTime
                        # Cadence
                        elif SENSOR_TYPE == CADENCE_DEVICE_TYPE:
                            if self.cadence_listener.lastTime == last_event:
                                # Set power to zero if cadence sensor doesn't update for 3 seconds
                                self.power_meter.powerData.instantaneousPower = 0
                                stopped = True
                            last_event = self.cadence_listener.lastTime
                        
                        last_time = t

                    # Force an update every second to avoid power drops
                    power = self.power_meter.powerData.instantaneousPower
                    cadence = self.cadence_listener.cadence
                    revolutions = self.cadence_listener.revolutions
                    speed = 0.259 * cadence + 0.674

                    self.power_meter.update(power)
                    self.speed_sensor.update(revolutions * 13)

                    print(f'Power: {int(power)} W, Cadence: {int(cadence)} RPM, Speed: {int(speed)} MPH   \r', end="")
                elif self.power_meter.powerData.instantaneousPower:
                    stopped = False
                time.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                break