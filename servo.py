import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
class Stepper:
    def __init__(self,DIR, STEP, slp):
        GPIO.setup(DIR, GPIO.OUT)
        GPIO.setup(STEP, GPIO.OUT)
        GPIO.setup(slp, GPIO.OUT)

        self.DIR = DIR
        self.STEP = STEP
        self.slp = slp

        GPIO.output(self.slp, 1)

    def step(self):
        GPIO.output(self.STEP, 1)
        time.sleep(1e-6)
        GPIO.output(self.STEP, 0)

    def change_dir(self, val):
        GPIO.output(self.DIR, val)
    
    def off(self):
        GPIO.output(self.slp, 0)


if __name__ == "__main__":
    myserv = Stepper(17, 27, 22)
    for _ in range(4):
        for _ in range(2* 50 * 8):
            myserv.step()
            time.sleep(0.00025)
    myserv.change_dir(1)
    for _ in range(50 * 8):
        myserv.step()
        time.sleep(0.0025)
    myserv.off()

    GPIO.cleanup()