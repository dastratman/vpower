# Thanks to the original work of
# https://github.com/dhague/vpower

import sys
import time
from ant.core import message, node, driver
from ant.core.constants import *
from ant.core.exceptions import ChannelError

from constants import *
from config import NETKEY, VPOWER_DEBUG

CHANNEL_PERIOD = 8118

# Transmitter for Bicycle Speed ANT+ sensor
class SpeedTx(object):

    class SpeedData:
        def __init__(self):
            self.eventCount = 0
            self.totalRevolutions = 0
            self.myNow = time.time()
            self.oldNow = time.time()

    def __init__(self, antnode, sensor_id):
        self.antnode = antnode

        # Get the channel
        self.channel = antnode.getFreeChannel()
        try:
            self.channel.name = 'C:SPEED'
            network = node.Network(NETKEY, 'N:ANT+')
            self.channel.assign(network, CHANNEL_TYPE_TWOWAY_TRANSMIT)
            self.channel.setID(SPEED_DEVICE_TYPE, sensor_id, 0)
            self.channel.period = CHANNEL_PERIOD
            self.channel.frequency = 57
        except ChannelError as e:
            print ("Channel config error: "+e.message)

        self.speedData = SpeedTx.SpeedData()

    def open(self):
        self.channel.open()

    def close(self):
        self.channel.close()

    def unassign(self):
        self.channel.unassign()

    def update(self, myWheel, mySpeed):

	# input mySpeed must be millimeters/sec
	# Then how much time a wheel rotation ?
	# Please in milliseconds ... and standard wheel in Simulant is 2200000 micrometers

        myTick = myWheel / mySpeed

	#
	# Bike Speed Event Time
	# Tricky stuff. Must add to previous time the rotation time
	# but I have milliseconds to be converted to (sic!)  1/1024 sec
	# then mod 65536 because of the two bytes range
	#

        self.speedData.myNow = self.speedData.oldNow + myTick
        self.speedData.oldNow = self.speedData.myNow
        antSlot = int(((self.speedData.myNow / 1000)  % 64) * 1024)

	# and of course add 1 revolution

        self.speedData.totalRevolutions += 1

        # payloads

        myP4 = (antSlot & 0xff)
        myP5 = (antSlot >> 8)
        myP6 = (self.speedData.totalRevolutions & 0xff)
        myP7 = (self.speedData.totalRevolutions >> 8)

        try:

           self.speedData.eventCount = (self.speedData.eventCount + 1) & 0xff
           myPayload = [0x00]
#
#   3 byte reserved and set to FF
#
           myPayload.append(0xff)
           myPayload.append(0xff)
           myPayload.append(0xff)

           myPayload.append(myP4)
           myPayload.append(myP5)
           myPayload.append(myP6)
           myPayload.append(myP7)

           payload = bytearray(myPayload)
           ant_msg = message.ChannelBroadcastDataMessage(self.channel.number, data=payload)
           self.antnode.send(ant_msg)

        except Exception as e:
               print ("Exception in SpeedTX: "+repr(e))

