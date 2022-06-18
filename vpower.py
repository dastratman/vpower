#!/usr/bin/env python
import sys

from AntDevice import AntDevice

antdevice = AntDevice()

try:
    antdevice.start_ant()
    antdevice.start_sensor()
    antdevice.start_power_meter()
    antdevice.register_callbacks()
    antdevice.wait_loop()
except Exception as e:
    print("Exception: " + repr(e))
    if getattr(sys, 'frozen', False):
        input()
finally:
    if not antdevice.pywin32:
        antdevice.stop_ant()
