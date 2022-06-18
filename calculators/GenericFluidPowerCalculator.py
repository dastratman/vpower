from calculators.AbstractPowerCalculator import AbstractPowerCalculator
from functions import interp


'''
Generic fluid trainer power calculator.
'''
class GenericFluidPowerCalculator(AbstractPowerCalculator):
    def __init__(self):
        super(GenericFluidPowerCalculator, self).__init__()
        self.wheel_circumference = 2.105  # default value - can be overridden in config.py

    # Data from Generic Fluid:
    # http://www.powercurvesensor.com/cycling-trainer-power-curves/
    # speed values
    xp = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0]
    # power values
    yp = [0.0, 25.0, 50.0, 85.0, 110.0, 160.0, 220.0, 300.0, 410.0, 550.0, 700.0, 890.0, 1100.0]

    def power_from_speed(self, revs_per_sec):
        kms_per_rev = self.wheel_circumference / 1000.0
        speed = revs_per_sec * 3600 * kms_per_rev
        power = int(interp(self.xp, self.yp, speed))
        return power

    def set_wheel_circumference(self, circumference):
        self.wheel_circumference = circumference
