import os, sys
import csv
from calculators.AbstractPowerCalculator import AbstractPowerCalculator
from functions import interp

if getattr(sys, 'frozen', False):
    # If we're running as a pyinstaller bundle
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

class LinearInterpolationPowerCalculator(AbstractPowerCalculator):
    def __init__(self):
        super(LinearInterpolationPowerCalculator, self).__init__()
        self.wheel_circumference = 2.105  # default value - can be overridden in config.py

    xp = [0]
    yp = [0]
    curve_file = '%s/curves/curve.csv' % SCRIPT_DIR
    if os.path.isfile(curve_file):
        with open(curve_file, 'r') as fd:
            reader = csv.reader(fd)
            next(reader, None)
            for line in reader:
                xp.append(int(line[0]))
                yp.append(int(line[1]))
    else:
        xp.extend([5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60])
        yp.extend([30, 60, 90, 125, 160, 200, 230, 280, 325, 375, 430, 490])

    def power_from_speed(self, revs_per_sec):
        kms_per_rev = self.wheel_circumference / 1000.0
        speed = revs_per_sec * 3600 * kms_per_rev
        power = int(interp(self.xp, self.yp, speed))
        return power

    def set_wheel_circumference(self, circumference):
        self.wheel_circumference = circumference
