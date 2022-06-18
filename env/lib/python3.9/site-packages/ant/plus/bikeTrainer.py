# -*- coding: utf-8 -*-

from .plus import DeviceProfile
from .genericFEC import genericFEC

#################################################################################################

class bikeTrainer(DeviceProfile):
    channelPeriod = 8192
    deviceType = 0x11                     #FE-C
    name = 'Stationary Bike'


    def __init__(self, node, network, callbacks=None):
        super(bikeTrainer, self).__init__(node, network, callbacks)

        self.page16 = genericFEC()
        self._elapsedTime = 0.0
        self._distanceTraveled = 0
        self._instantaneousSpeed = 0.0
        self._kmSpeed = 0.0
        self._cadence = 0
        self._power = 0
        self._detected_device = None

    def event_time_correction(self, time_difference):
        return time_difference * 1000 / 1024

    def processData(self, data):
        with self.lock:
            dataPageNumber = data[0]

            if(dataPageNumber == 16):
               self.page16.p16(data)
               self._elapsedTime = self.page16.elapsedTime
               self._distanceTraveled = self.page16.distanceTraveled
               self._instantaneousSpeed = self.page16.instantaneousSpeed
               self._kmSpeed = self.page16.kmSpeed

            if(dataPageNumber == 25):
               self._cadence = data[2]
               self._power = data[5] + (256 * data[6])
               if (self._power == 65535):          ## FFFF invalid
                   self._power = 0.0
                   self._cadence = 0

            callback = self.callbacks.get('onBikeTrainer')
            if callback:
                callback(self._elapsedTime, self._distanceTraveled, self._instantaneousSpeed, self._kmSpeed, self._cadence, self._power)

