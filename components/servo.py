from rpi_hardware_pwm import HardwarePWM


class Servo:
    def __init__(self, pwm_channel, hz=50):
        self.pwm_channel = pwm_channel
        self.hz = hz
        self.angle = 90
        self.pwm = HardwarePWM(pwm_channel=self.pwm_channel, hz=self.hz, chip=0)
        self.pwm.start(self._angle_to_duty(self.angle))

    def _angle_to_duty(self, angle):
        """Convert a 0-180° servo position to a 50 Hz hardware PWM duty cycle."""
        clamped = max(0, min(180, angle))
        return 2.5 + (clamped / 180.0) * 10.0

    def set_pos(self, angle):
        self.angle = max(0, min(180, angle))
        self.pwm.change_duty_cycle(self._angle_to_duty(self.angle))

    def set_angle(self, angle):
        self.set_pos(angle)

    def stop(self):
        self.pwm.stop()

    def cleanup(self):
        self.stop()