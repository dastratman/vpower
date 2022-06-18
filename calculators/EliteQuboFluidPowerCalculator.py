from calculators.AbstractPowerCalculator import AbstractPowerCalculator


'''
Elite Qubo Fluid power calculator.
'''
class EliteQuboFluidPowerCalculator(AbstractPowerCalculator):
    def __init__(self):
        super(EliteQuboFluidPowerCalculator, self).__init__()
        self.wheel_circumference = 2.105  # default value - can be overridden in config.py

    # Data from powercurvesensor http://www.powercurvesensor.com/cycling-trainer-power-curves/
    # Fitted model is from Golden Cheetah https://github.com/GoldenCheetah/GoldenCheetah

    def power_from_speed(self, revs_per_sec):
        kms_per_rev = self.wheel_circumference / 1000.0
        speed = revs_per_sec * 3600 * kms_per_rev
        power = int(4.31746 * speed -2.59259e-002 * speed ** 2 +  9.41799e-003 * speed ** 3)
        return power

    def set_wheel_circumference(self, circumference):
        self.wheel_circumference = circumference