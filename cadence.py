#!/usr/bin/env python
import sys

from ant.core.constants import *

from AntDevice import AntDevice

antdevice = AntDevice()
try:
    antdevice.start_ant()
    antdevice.start_sensor()
    antdevice.start_power_meter()
    antdevice.start_speed_sensor()
    antdevice.register_callbacks()
    antdevice.wait_loop()
except Exception as e:
    print("Exception: " + repr(e))
    if getattr(sys, 'frozen', False):
        input()
finally:
    if not antdevice.pywin32:
        antdevice.stop_ant()