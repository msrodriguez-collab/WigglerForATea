import RPi.GPIO as GPIO
import time
import leddriver as LED

RED = 17
GREEN = 27
BLUE = 22

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)
freq = 2000
redpwm = GPIO.PWM(RED, freq)
greenpwm = GPIO.PWM(GREEN, freq)
bluepwm = GPIO.PWM(BLUE, freq)

hexcode = 0xFFD900
colorpurp = 0x8E0AF2
colorgreen = 0x76A635
colorwhite = 0xFFFFFF
colorred = 0xFF0000
coloryellow = 0xFFD900

red, green, blue = LED.colorduty(hexcode)

try: 
    while True: 
        red, green, blue = LED.colorduty(colorred)
        redpwm.start(red)
        greenpwm.start(green)
        bluepwm.start(blue)
        time.sleep(1)
        red, green, blue = LED.colorduty(coloryellow)
        redpwm.start(red)
        greenpwm.start(green)
        bluepwm.start(blue)
        time.sleep(1)
        red, green, blue = LED.colorduty(colorgreen)
        redpwm.start(red)
        greenpwm.start(green)
        bluepwm.start(blue)
        time.sleep(1)

finally:
    redpwm.stop()
    greenpwm.stop()
    bluepwm.stop()
    GPIO.cleanup()