import subprocess
import os
import fcntl
import sys

def reset_USB_Device():

    print(sys.version_info)
    if (sys.version_info < (3, 5)):
       print("Reset_USB_Device: Python 3.5 and above required ...")
       return(False)

    # Same as _IO('U', 20) constant in the linux kernel.
    CONST_USB_DEV_FS_RESET_CODE = ord('U') << (4*2) | 20
    USB_DEV_NAME = 'Dynastream'
    usb_dev_path = ""

    # Based on 'lsusb' command, get the usb device path in the following format -
    # /dev/bus/usb/<busnum>/<devnum>

    proc = subprocess.run(['lsusb'], capture_output=True, text=True)
    usb_device_list = proc.stdout.split('\n')
    for device in usb_device_list:
        if USB_DEV_NAME in device:
           print ("Found " + str(device))
           usb_dev_details = device.split()
           usb_bus = usb_dev_details[1]
           usb_dev = usb_dev_details[3][:3]
           usb_dev_path = '/dev/bus/usb/%s/%s' % (usb_bus, usb_dev)
    try:
       if usb_dev_path != "":
          print ("Trying to reset USB Device: " + usb_dev_path)
          device_file = os.open(usb_dev_path, os.O_WRONLY)
          fcntl.ioctl(device_file, CONST_USB_DEV_FS_RESET_CODE, 0)
          print ("USB Device reset successful.")
       else:
          print ("Device not found.")
    except:
          print ("Failed to reset the USB Device.")
    finally:
          try:
             os.close(device_file)
          except:
             pass

