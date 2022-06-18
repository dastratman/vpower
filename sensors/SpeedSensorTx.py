import sys
from ant.core import message, node
from ant.core.constants import *
from ant.core.exceptions import ChannelError
import time
from binascii import hexlify

from constants import *
from config import NETKEY, VPOWER_DEBUG

CHANNEL_PERIOD = 8182


# Transmitter for Bicycle Speed ANT+ sensor
class SpeedSensorTx(object):
    class SpeedData:
        def __init__(self):
            self.revCounts = 0
            self.ucMessageCount = 0
            self.ulRunTime = 0
            self.ucPageChange = 0
            self.ucExtMesgType = 1

    def __init__(self, antnode, sensor_id, wheel = 0.100):
        self.antnode = antnode
        self.speed = 0
        self.lastTime = 0
        self.wheel = wheel
        self.remWay = 0
        self.sensor_id = sensor_id

        # Get the channel
        self.channel = antnode.getFreeChannel()
        try:
            self.channel.name = 'C:SPEED'
            network = node.Network(NETKEY, 'N:ANT+')
            self.channel.assign(network, CHANNEL_TYPE_TWOWAY_TRANSMIT)
            self.channel.setID(SPEED_DEVICE_TYPE, sensor_id & 0xFFFF, 1)
            self.channel.period = CHANNEL_PERIOD
            self.channel.frequency = 57
        except ChannelError as e:
            print("Channel config error: " + repr(e))
        self.speedData = SpeedSensorTx.SpeedData()

    def open(self):
        self.channel.open()

    def close(self):
        self.channel.close()

    def unassign(self):
        self.channel.unassign()

    # Speed was updated, so send out an ANT+ message
    # https://github.com/haraldh/iconsole
    def update(self, revolutions):
        now = time.time()
        usTime1024 = int(now * 1024)

        self.speedData.revCounts = revolutions
        # self.speedData.revCounts += int(revolutions)
        self.speedData.ucPageChange += 0x20;
        self.speedData.ucPageChange &= 0xF0;
        self.speedData.ucMessageCount += 1

        if VPOWER_DEBUG: print('SpeedSensorTx: update called with revolutions ', revolutions)
        if VPOWER_DEBUG: print('revCounts ', self.speedData.revCounts)
        if VPOWER_DEBUG: print('ucMessageCount ', self.speedData.ucMessageCount)
        if VPOWER_DEBUG: print('ucExtMesgType ', self.speedData.ucExtMesgType)
        if VPOWER_DEBUG: print('ucPageChange ', self.speedData.ucPageChange)

        if self.speedData.ucMessageCount >= 65:
            self.speedData.ucPageChange = 0x20;
            self.speedData.ucPageChange &= 0xF0;

            if self.speedData.ucExtMesgType >= 4:
                self.speedData.ucExtMesgType = 1

            if self.speedData.ucExtMesgType == 1:
                ulElapsedTime2 = int(now/2.0)
                payload = bytearray(bytes(0x01 | (self.speedData.ucPageChange & 0x80)))
                payload.append((ulElapsedTime2) & 0xFF)
                payload.append((ulElapsedTime2 >> 8) & 0xFF)
                payload.append((ulElapsedTime2 >> 16) & 0xFF)
            elif self.speedData.ucExtMesgType == 2:
                payload = bytearray(bytes(0x02 | (self.speedData.ucPageChange & 0x80)))
                payload.append(0xFF) # MID
                payload.append((self.sensor_id >> 16) & 0xFF) # Serial 17-24
                payload.append((self.sensor_id >> 24) & 0xFF) # Serial 25-32
            elif self.speedData.ucExtMesgType == 3:
                payload = bytearray(bytes(0x03 | (self.speedData.ucPageChange & 0x80)))
                payload.append(0x01) # HW
                payload.append(0x01) # SW
                payload.append(0x01) # Model

            if self.speedData.ucMessageCount >= 68:
                self.speedData.ucMessageCount = 0   
                self.speedData.ucExtMesgType += 1
        else:
            payload = bytearray(bytes(self.speedData.ucPageChange & 0x80))
            payload.append(0xFF)
            payload.append(0xFF)
            payload.append(0xFF)

        # print("Broadcast: %s" % hexlify(payload))

        
        payload.append(usTime1024 & 0xff)
        payload.append((usTime1024 >> 8) & 0xff)
        payload.append(self.speedData.revCounts & 0xff)
        payload.append((self.speedData.revCounts >> 8) & 0xff)

        # """
        # payload = bytearray(bytes(0x20 & 0x80))
        payload = bytearray(b'\x80')  # standard speed-only message
        payload.append(0xFF)
        payload.append(0xFF)
        payload.append(0xFF)
        payload.append(usTime1024 & 0xff)
        payload.append((usTime1024 >> 8) & 0xff)
        payload.append(self.speedData.revCounts & 0xff)
        payload.append((self.speedData.revCounts >> 8) & 0xff)
        # """ 

        if VPOWER_DEBUG: print("Broadcast (speed): %s" % hexlify(payload))
        ant_msg = message.ChannelBroadcastDataMessage(self.channel.number, data=payload)

        if VPOWER_DEBUG: print('Write message to ANT stick on channel ' + repr(self.channel.number))
        self.antnode.send(ant_msg)
