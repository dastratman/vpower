# ANT+ Virtual Power Meter

## Overview

This project implements "virtual power" for bicycle turbo trainers where the trainer or the attached bike has an ANT+ 
speed sensor. The calculated power is broadcasted as such on ANT+ (using [python-ant](https://github.com/mvillalba/python-ant)) so that any head unit or app will see it as a power
meter.

This version (forked from [vpower](https://github.com/dhague/vpower) by Darren Hague) is adapted to run on Windows.

The **bot** version is for testing purposes, you can set the power value in a slider.

The **heartrate** version broadcasts power based on heart rate, set the values in the file [zones.csv](https://github.com/oldnapalm/vpower/blob/master/zones.csv)

The **cadence** version broadcasts power based on cadence, set the values in the file [cadence.csv](https://github.com/oldnapalm/vpower/blob/master/cadence.csv)

The **row** version supports the [Concept2 Rowing Ergometer](https://www.concept2.com/indoor-rowers) (uses [PyRow](https://github.com/wemakewaves/PyRow)).
Thanks Jonathan Colledge for testing and debugging.

Even if the receiver app runs on the same computer, you will need two ANT+ sticks, because one device can't be used by two apps simultaneously.

Currently supported trainers:
* [Bike Technologies Advanced Training System (BT-ATS)](http://www.biketechnologies.com/bt-advanced-training-system/)
* [CycleOps Fluid2](https://www.cycleops.com/product/fluid2)
* [Elite Novo Force 8](https://www.elite-it.com/en/products/home-trainers/classic-trainers/novo-force)
* [Elite Qubo Fluid](https://www.elite-it.com/en/products/home-trainers/classic-trainers/qubo-fluid)
* [Generic Fluid](http://www.powercurvesensor.com/cycling-trainer-power-curves/)
* [Generic Magnetic (medium resistance)](http://www.powercurvesensor.com/cycling-trainer-power-curves/)
* [Kurt Kinetic range of fluid trainers](https://kurtkinetic.com/products/trainers/)
* [Tacx Blue Motion](https://tacx.com/product/blue-motion/)

It is easy to add a new trainer - just subclass `AbstractPowerCalculator` and implement the method `power_from_speed(revs_per_sec)`.
If your trainer is not there, please add it and submit a pull request.

Supported devices:
* [ANTUSB2 Stick](http://www.thisisant.com/developer/components/antusb2/) (0fcf:1008: Dynastream Innovations, Inc.)
* [ANTUSB-m Stick](http://www.thisisant.com/developer/components/antusb-m/) (0fcf:1009: Dynastream Innovations, Inc.)

Warning: the [Cycplus ANT Stick](https://tacxfaqx.com/knowledge-base/cycplus-ant-stick/) is not compatible, even though it uses the same Vendor ID and Product ID (0fcf:1008) as the ANTUSB2 Stick.

## Running on Windows

* Download the [standalone executable](https://github.com/oldnapalm/vpower/releases/latest)
* Configure speed sensor, power calculator and wheel circumference in **vpower.cfg**
  * You can leave `sensor_id` as zero if there's only one sensor around
  * If using `LinearInterpolationPowerCalculator` set speed and power values in the file [curve.csv](https://github.com/oldnapalm/vpower/blob/master/curve.csv)
* Install the libusb-win32 driver for the ANT+ device (if not already installed), it can be easily done using [Zadig](https://zadig.akeo.ie/)
  * Options - List All Devices
  * Select ANT+ stick
  * Select libusb-win32 driver and click Replace Driver
* If using the row version, install the libusb-win32 driver for the rower too
* Run the downloaded executable

## Running from source code (Windows, Linux, macOS)

* Install [Python 3](https://www.python.org/downloads/) if not already installed
  * Check "Add Python to PATH" or use the full path in the commands below
* Clone or download this repo
* CD to the repo directory and run `pip install -r requirements.txt`
  * On Linux and macOS use `pip3` instead of `pip`
* [Optional] Run `pip install pywin32` (Windows only, to stop the ANT node on terminal window close)
* Run `python vpower.py` (or double click **vpower.py** if you installed the Python Launcher)
  * On Linux and macOS use `python3` instead of `python`
