import board
import busio
from adafruit_pca9685 import PCA9685 as AdafruitPCA9685


class PCA9685Board:
    def __init__(self, address=0x40, frequency=50):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.device = AdafruitPCA9685(self.i2c, address=address)
        self.frequency = frequency
        self.device.frequency = frequency

    def set_duty_cycle(self, channel, duty_cycle):
        if not 0 <= channel < 16:
            raise ValueError("PCA9685 channel must be between 0 and 15")
        if not 0 <= duty_cycle <= 0xFFFF:
            raise ValueError("Duty cycle must be between 0 and 65535")

        self.device.channels[channel].duty_cycle = int(duty_cycle)

    def cleanup(self):
        self.device.deinit()
        self.i2c.deinit()
