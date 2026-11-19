import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
class A4988_Stepper:
    def __init__(self,DIR, STEP, slp):
        GPIO.setup(DIR, GPIO.OUT)
        GPIO.setup(STEP, GPIO.OUT)
        GPIO.setup(slp, GPIO.OUT)

        self.DIR = DIR
        self.STEP = STEP
        self.slp = slp

        GPIO.output(self.slp, 0)

    def step(self):
        GPIO.output(self.STEP, 1)
        time.sleep(1e-6)
        GPIO.output(self.STEP, 0)

    def change_dir(self, val):
        GPIO.output(self.DIR, val)
    
    def off(self):
        GPIO.output(self.slp, 0)

class A4988_Double_Stepper:
    def __init__(self, DIR, STEP1, STEP2, EN):
        GPIO.setup(DIR, GPIO.OUT)
        GPIO.setup(STEP1, GPIO.OUT)
        GPIO.setup(STEP2, GPIO.OUT)
        GPIO.setup(EN, GPIO.OUT)

        self.DIR = DIR
        self.STEP1 = STEP1
        self.STEP2 = STEP2
        self.EN = EN

        GPIO.output(self.DIR, 0)
        GPIO.output(self.EN, 0)

    def step1(self):
        GPIO.output(self.STEP1, 1)
        time.sleep(1e-6)
        GPIO.output(self.STEP1, 0)

    def step2(self):
        GPIO.output(self.STEP2, 1)
        time.sleep(1e-6)
        GPIO.output(self.STEP2, 0)

    def change_dir(self, val):
        GPIO.output(self.DIR, val)
    
    def off(self):
        GPIO.output(self.EN, 1)

    def on(self):
        GPIO.output(self.EN, 0)


if __name__ == "__main__":
    myserv = A4988_Double_Stepper(17, 27, 23, 24)
    delay = 0.001
    MICROSTEPS = 16

    for _ in range(MICROSTEPS * 200):
        myserv.step1()
        time.sleep(delay)
    for _ in range(MICROSTEPS * 50 * 2):
        myserv.step2()
        time.sleep(delay)
    myserv.change_dir(1)
    for _ in range(MICROSTEPS * 50 * 2):
        myserv.step1()
        time.sleep(delay)
    for _ in range(MICROSTEPS * 50 * 2):
        myserv.step2()
        time.sleep(delay)
    myserv.change_dir(0)
    for _ in range(MICROSTEPS * 50 * 2):
        myserv.step1()
        myserv.step2()
        time.sleep(delay)
    for _ in range(MICROSTEPS * 50 * 2):
        myserv.step1()
        myserv.step2()
        time.sleep(delay)
    for _ in range(MICROSTEPS * 50 * 2):
        myserv.change_dir(0)
        myserv.step1()
        myserv.change_dir(1)
        myserv.step2()
        time.sleep(delay)
    for _ in range(MICROSTEPS * 50 * 2):
        myserv.change_dir(1)
        myserv.step1()
        myserv.change_dir(0)
        myserv.step2()
        time.sleep(delay)
    myserv.off()

    GPIO.cleanup()