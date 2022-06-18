import os, sys
import csv
from ant.core import driver, node, event, message
from functions import interp

if getattr(sys, 'frozen', False):
    # If we're running as a pyinstaller bundle
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def convertSB(raw):
    value = int(raw[1]) << 8
    value += int(raw[0])
    return value

class CadenceListener(event.EventCallback):
    def __init__(self, power_meter, speed_sensor):
        self.lastTime = None
        self.lastRevolutions = None
        self.revolutions = None
        self.power_meter = power_meter
        self.speed_sensor = speed_sensor
        self.cadence = 0

        self.xp = [0]
        self.yp = [0]

    def load_power_curve(self):
        cadence_file = '%s/curves/cadence.csv' % SCRIPT_DIR
        if os.path.isfile(cadence_file):
            with open(cadence_file, 'r') as fd:
                reader = csv.reader(fd)
                next(reader, None)
                for line in reader:
                    self.xp.append(int(line[0]))
                    self.yp.append(int(line[1]))
        else:
            self.xp.extend([20, 40, 60, 80, 100, 120, 140])
            self.yp.extend([40, 80, 100, 200, 400, 600, 800])

    def calcCadence(self, time, revolutions):
        if self.lastTime is None:
            return 0

        if time < self.lastTime:
            time += 65536

        if revolutions < self.lastRevolutions:
            revolutions += 65536

        return (revolutions - self.lastRevolutions) * 1024 * 60 / (time - self.lastTime)

    def process(self, msg):
        if isinstance(msg, message.ChannelBroadcastDataMessage):
            page = msg.payload[1] & 0x7F
            if page != 0:
                return

            eventTime = convertSB(msg.payload[5:7])
            if eventTime == self.lastTime:
                return

            self.revolutions = convertSB(msg.payload[7:9])

            self.cadence = self.calcCadence(eventTime, self.revolutions)

            power = int(interp(self.xp, self.yp, self.cadence))
            self.power_meter.update(power)

            self.speed_sensor.update(self.revolutions * 13)

            self.lastTime = eventTime
            self.lastRevolutions = self.revolutions