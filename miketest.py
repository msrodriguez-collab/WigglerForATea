import RPi.GPIO as GPIO
from rpi_hardware_pwm import HardwarePWM
import time

GPIO.setmode(GPIO.BCM)

servo1 = HardwarePWM(pwm_channel=2, hz=50, chip=0)
servo2 = HardwarePWM(pwm_channel=3, hz=50, chip=0)

servo1.start(11)
servo2.start(5)
servo1.start(5)
exit(0)

def turnhand(start, end, tottime, roughness=0.025):
    N = int(tottime / roughness)
    for i in range(N + 1):
        pwmduty = start + (i / N) * (end-start)
        servo2.change_duty_cycle(pwmduty)
        time.sleep(roughness)

time.sleep(3)

try:
    servo1.change_duty_cycle(6)
    time.sleep(1)
    turnhand(5, 10, 0.5)
    time.sleep(1)
    servo1.change_duty_cycle(11)
    time.sleep(1)
    turnhand(10, 5, 0.5)
    time.sleep(1)
finally:
    servo1.stop()
    servo2.stop()

GPIO.cleanup()