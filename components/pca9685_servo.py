from components.pca9685 import PCA9685Board


class PCA9685Servo:
    def __init__(
        self,
        pca: PCA9685Board,
        channel,
        min_angle=0,
        max_angle=180,
        min_pulse_us=500,
        max_pulse_us=2500,
    ):
        if min_angle >= max_angle:
            raise ValueError("min_angle must be less than max_angle")
        if min_pulse_us <= 0 or min_pulse_us >= max_pulse_us:
            raise ValueError("Pulse widths must be positive and increasing")

        self.pca = pca
        self.channel = channel
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.min_pulse_us = min_pulse_us
        self.max_pulse_us = max_pulse_us
        self.angle = None

    def set_pos(self, angle):
        angle = max(self.min_angle, min(self.max_angle, angle))
        angle_fraction = (angle - self.min_angle) / (self.max_angle - self.min_angle)
        pulse_us = self.min_pulse_us + angle_fraction * (
            self.max_pulse_us - self.min_pulse_us
        )
        period_us = 1_000_000 / self.pca.frequency
        duty_cycle = round(pulse_us * 0xFFFF / period_us)

        self.pca.set_duty_cycle(self.channel, duty_cycle)
        self.angle = angle

    def set_angle(self, angle):
        self.set_pos(angle)

    def stop(self):
        self.pca.set_duty_cycle(self.channel, 0)

    def cleanup(self):
        self.stop()
