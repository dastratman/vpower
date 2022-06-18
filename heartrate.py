#!/usr/bin/env python
import os, sys
import time
import csv
import platform

from ant.core import driver
from ant.core import node
from ant.plus.heartrate import *

from usb.core import find

from sensors.PowerMeterTx import PowerMeterTx
from config import DEBUG, LOG, NETKEY, POWER_SENSOR_ID
from functions import interp

if getattr(sys, 'frozen', False):
    # If we're running as a pyinstaller bundle
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

antnode = None
hr_monitor = None
power_meter = None

last = 0
stopped = True

xp = [0]
yp = [0]
zones_file = '%s/curves/zones.csv' % SCRIPT_DIR
if os.path.isfile(zones_file):
    with open(zones_file, 'r') as fd:
        reader = csv.reader(fd)
        next(reader, None)
        for line in reader:
            xp.append(int(line[0]))
            yp.append(int(line[1]))
else:
    xp.extend([80, 100, 120, 140, 160, 180])
    yp.extend([0, 110, 140, 170, 200, 230])

def stop_ant():
    if hr_monitor:
        print("Closing heart rate monitor")
        hr_monitor.close()
    if power_meter:
        print("Closing power meter")
        power_meter.close()
        power_meter.unassign()
    if antnode:
        print("Stopping ANT node")
        antnode.stop()

pywin32 = False
if platform.system() == 'Windows':
    def on_exit(sig, func=None):
        stop_ant()
    try:
        import win32api
        win32api.SetConsoleCtrlHandler(on_exit, True)
        pywin32 = True
    except ImportError:
        print("Warning: pywin32 is not installed, use Ctrl+C to stop")

def heart_rate_data(computed_heartrate, event_time_ms, rr_interval_ms):
    global last
    global stopped
    t = int(time.time())
    if t >= last + 1:
        power = int(interp(xp, yp, computed_heartrate))
        if power:
            power_meter.update(power)
            stopped = False
        elif not stopped:
            power_meter.update(power)
            stopped = True
        last = t

try:
    devs = find(find_all=True, idVendor=0x0fcf)
    for dev in devs:
        if dev.idProduct in [0x1008, 0x1009]:
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

    antnode = node.Node(stick)
    print("Starting ANT node")
    antnode.start()
    network = node.Network(NETKEY, 'N:ANT+')
    antnode.setNetworkKey(0, network)

    print("Starting power meter with ANT+ ID " + repr(POWER_SENSOR_ID))
    try:
        # Create the power meter object and open it
        power_meter = PowerMeterTx(antnode, POWER_SENSOR_ID)
        power_meter.open()
    except Exception as e:
        print("power_meter error: " + repr(e))
        power_meter = None

    print("Starting heart rate monitor")
    try:
        # Create the heart rate monitor object and open it
        hr_monitor = HeartRate(antnode, network, {'onHeartRateData': heart_rate_data})
        hr_monitor.open()
    except Exception as e:
        print("hr_monitor error: " + repr(e))
        hr_monitor = None

    print("Main wait loop")
    while True:
        try:
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            break

except Exception as e:
    print("Exception: " + repr(e))
    if getattr(sys, 'frozen', False):
        input()
finally:
    if not pywin32:
        stop_ant()
