from configparser import ConfigParser

import os, sys
from ant.core import log

from calculators.BtAtsPowerCalculator import BtAtsPowerCalculator
from calculators.CycleOpsFluid2PowerCalculator import CycleOpsFluid2PowerCalculator
from calculators.EliteNovoForceS3PowerCalculator import EliteNovoForceS3PowerCalculator
from calculators.EliteQuboFluidPowerCalculator import EliteQuboFluidPowerCalculator
from calculators.GenericFluidPowerCalculator import GenericFluidPowerCalculator
from calculators.GenericMagneticPowerCalculator import GenericMagneticPowerCalculator
from calculators.KurtKineticPowerCalculator import KurtKineticPowerCalculator
from calculators.LinearInterpolationPowerCalculator import LinearInterpolationPowerCalculator
from calculators.TacxBlueMotionPowerCalculator import TacxBlueMotionPowerCalculator

from constants import *
import hashlib

if getattr(sys, 'frozen', False):
    # If we're running as a pyinstaller bundle
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

VPOWER_DEBUG = False

# ANT+ ID of the virtual power sensor
# The expression below will choose a fixed ID based on the CPU's serial number
POWER_SENSOR_ID = int(int(hashlib.md5(getserial().encode()).hexdigest(), 16) & 0xfffe) + 1

# Set to None to disable ANT+ message logging
LOG = None
# LOG = log.LogWriter(filename="vpower.log")

# ANT+ network key
NETKEY = b'\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'

if LOG:
    print("Using log file:", LOG.filename)
    print("")

_CONFIG_FILENAME = os.path.join(SCRIPT_DIR, 'vpower.cfg')

if os.path.isfile(_CONFIG_FILENAME):
    CONFIG = ConfigParser()

    SECTION = 'vpower'

    if VPOWER_DEBUG: print('Read config file')
    CONFIG.read(_CONFIG_FILENAME)

    if VPOWER_DEBUG: print('Get config items')

    # Type of sensor connected to the trainer
    SENSOR_TYPE = CONFIG.getint(SECTION, 'sensor_type')

    # ANT+ ID
    SENSOR_ID = CONFIG.getint(SECTION, 'sensor_id')
    SPEED_SENSOR_ID = CONFIG.getint(SECTION, 'speed_sensor_id')

    # ANT+ channel
    SENSOR_CHANNEL = CONFIG.get(SECTION, 'sensor_channel')

    # Calculator for the model of turbo
    pc_class = globals()[CONFIG.get(SECTION, 'power_calculator')]
    POWER_CALCULATOR = pc_class()

    # For wind/air trainers, current air density in kg/m3 (if not using a BME280 weather sensor)
    POWER_CALCULATOR.air_density = CONFIG.getfloat(SECTION, 'air_density')

    # For wind/air trainers, how often (secs) to update the air density if there *is* a BME280 present
    POWER_CALCULATOR.air_density_update_secs = CONFIG.getfloat(SECTION, 'air_density_update_secs')

    # For tyre-driven trainers, the wheel circumference in meters (2.122 for Continental Home trainer tyre)
    POWER_CALCULATOR.wheel_circumference = CONFIG.getfloat(SECTION, 'wheel_circumference')

    # Overall correction factor, e.g. to match a user's power meter on another bike
    POWER_CALCULATOR.set_correction_factor(CONFIG.getfloat(SECTION, 'correction_factor'))

    # If set to True, the stick's driver will dump everything it reads/writes from/to the stick.
    DEBUG = CONFIG.getboolean(SECTION, 'debug')

else:
    if VPOWER_DEBUG: print('Config file not found, using default values')
    SENSOR_TYPE = 123
    SENSOR_ID = 0
    POWER_CALCULATOR = LinearInterpolationPowerCalculator()
    POWER_CALCULATOR.air_density = 1.191
    POWER_CALCULATOR.air_density_update_secs = 10
    POWER_CALCULATOR.wheel_circumference = 2.105
    POWER_CALCULATOR.set_correction_factor(1.0)
    DEBUG = VPOWER_DEBUG

POWER_CALCULATOR.set_debug(DEBUG)
