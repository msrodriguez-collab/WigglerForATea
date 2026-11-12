import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(14, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)

pw1 = GPIO.PWM(14, 50)
pw1.start(0)

pw2 = GPIO.PWM(15, 50)
pw2.start(0)



#pw1.ChangeDutyCycle(0.05)
pw2.ChangeDutyCycle(5)
time.sleep(1)
pw1.ChangeDutyCycle(5)
time.sleep(1)
pw2.ChangeDutyCycle(10)
time.sleep(1)
pw1.ChangeDutyCycle(10)
time.sleep(1)
GPIO.cleanup()