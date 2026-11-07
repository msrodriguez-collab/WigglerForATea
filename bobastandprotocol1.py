import board
import busio
from adafruit_pca9685 import PCA9685
import adafruit_motor.stepper as stepper
import leddriver as LED
import RPi.GPIO as GPIO
import time

#draft of the boba stand protocol
#using PCA9685 for LED control
#using A4988 for stepper motor control, one motor for turntable and one for auger. Two GPIO pins for step, sharing direction pin for both motors
#Also using PCA9685 for pumps and stirrer control
#using 4 GPIO pins for servo motors: one to lower stirrer, 3 for the mechanical arm
TURNTABLE = 17
AUGER = 27
DIRECTION = 4
STIRRER_SERVO = 5
CLAW_SERVO = 6
JOINT_SERVO1 = 13
JOINT_SERVO2 = 19

GPIO.setmode(GPIO.BCM)
GPIO.setup(STIRRER_SERVO, GPIO.OUT)
GPIO.setup(CLAW_SERVO, GPIO.OUT)
GPIO.setup(JOINT_SERVO1, GPIO.OUT)
GPIO.setup(JOINT_SERVO2, GPIO.OUT)

#setting up PWM for the pumps and stirrer
stirrer_servo = GPIO.PWM(STIRRER_SERVO, 50)
claw_servo = GPIO.PWM(CLAW_SERVO, 50)
joint_servo1 = GPIO.PWM(JOINT_SERVO1, 50)
joint_servo2 = GPIO.PWM(JOINT_SERVO2, 50)
#setting up stepper motors for turntable and auger
turntable = stepper.Stepper(step_pin=TURNTABLE, direction_pin=DIRECTION)
auger = stepper.Stepper(step_pin=AUGER, direction_pin=DIRECTION)

#setting up PCA9685 for LED control
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 1000  # Set the PWM frequency to 1 kHz
#using pins 1-6 for the RGB LEDs
#1-3 are for the flavor indicator, 4-6 are for the progress indicator
#using pins 7-9 for the pumps and 10 for the stirrer
RED1 = 1
GREEN1 = 2
BLUE1 = 3
RED2 = 4
GREEN2 = 5
BLUE2 = 6
PUMP_TARO = 7
PUMP_MATCHA = 8
PUMP_MILK = 9
STIRRER = 10

#colors
colortaro = 0x8E0AF2
colormatcha = 0x76A635
colormilk = 0xFFFFFF
colorred = 0xFF0000
coloryellow = 0xFFD900
colorgreen = 0x00FF00
colorblue = 0x0000FF

try:

    flavor_input = input("Enter flavor (taro, matcha, milk): ").strip().lower()
    boba_amount = int(input("Enter amount of boba (100%, 50%, 25%, 0%): ").strip().replace("%", ""))
    if flavor_input == "taro":
        red, green, blue = LED.colorduty(colortaro)
        pca.channels[RED1].duty_cycle = red * 65535 / 100
        pca.channels[GREEN1].duty_cycle = green * 65535 / 100
        pca.channels[BLUE1].duty_cycle = blue * 65535 / 100
    elif flavor_input == "matcha":
        red, green, blue = LED.colorduty(colormatcha)
        pca.channels[RED1].duty_cycle = red * 65535 / 100
        pca.channels[GREEN1].duty_cycle = green * 65535 / 100
        pca.channels[BLUE1].duty_cycle = blue * 65535 / 100
    elif flavor_input == "milk":
        red, green, blue = LED.colorduty(colormilk)
        pca.channels[RED1].duty_cycle = red * 65535 / 100
        pca.channels[GREEN1].duty_cycle = green * 65535 / 100
        pca.channels[BLUE1].duty_cycle = blue * 65535 / 100

    #starting the protocol, progress indicator will be red at the start
    red, green, blue = LED.colorduty(colorred)
    pca.channels[RED2].duty_cycle = red * 65535 / 100
    pca.channels[GREEN2].duty_cycle = green * 65535 / 100
    pca.channels[BLUE2].duty_cycle = blue * 65535 / 100

    #turning the turntable by 90 degrees
    turntable.step(50)
    #dispensing boba from the auger based on the amount of boba selected
    if boba_amount == 100:
        auger.step(800)
    elif boba_amount == 50:
        auger.step(400)
    elif boba_amount == 25:
        auger.step(200)
    elif boba_amount == 0:
        auger.step(0)
    #turning 90 degrees to the next position
    turntable.step(50)
    #dispensing tea based on the flavor selected
    if flavor_input == "taro":
        pca.channels[PUMP_TARO].duty_cycle = 65535
        time.sleep(5)
        pca.channels[PUMP_TARO].duty_cycle = 0
    elif flavor_input == "matcha":
        pca.channels[PUMP_MATCHA].duty_cycle = 65535
        time.sleep(5)
        pca.channels[PUMP_MATCHA].duty_cycle = 0
    elif flavor_input == "milk":
        pca.channels[PUMP_MILK].duty_cycle = 65535
        time.sleep(5)
        pca.channels[PUMP_MILK].duty_cycle = 0
    #switching progress indicator to yellow
    red, green, blue = LED.colorduty(coloryellow)
    pca.channels[RED2].duty_cycle = red * 65535 / 100
    pca.channels[GREEN2].duty_cycle = green * 65535 / 100
    pca.channels[BLUE2].duty_cycle = blue * 65535 / 100
    #turning 90 degrees to the next position
    turntable.step(50)
    #lowering the stirring arm and starting the stirrer
    stirrer_servo.start(7.5)  #CHANGE THIS!!!!!! This is just a PLACeHOLDER!!!!!!!!
    time.sleep(1)  # Wait for the servo to move
    pca.channels[STIRRER].duty_cycle = 65535  # Start the stirrer
    time.sleep(5)  # Stir for 5 seconds
    pca.channels[STIRRER].duty_cycle = 0  # Stop the stirrer
    stirrer_servo.start(2.5)  #ALSO AN PLACEHOLDER!!!!!!!!!! PLEASE for the LOVE OF GOD CHANGE THIS!!!!!!!!!!!!!
    time.sleep(1)  # Wait for the servo to move
    #after this, we will need to determine the servo protocol to move the arm
    #no clue how to do this yet, will probably need trial and error
    #also, all PWM values for pumps and stirrer are placeholders, will need to be determined by trial and error as well
    #REMEMBER TO CHANGE!!!!!! PLEASE FELIX!!!!!!! OR WHOEVER HAPPENS TO BE WORKING ON THIS NEXT!!!!!!!!!!!!!


finally:
    #cleaning up GPIO and stopping all PWM
    pca.deinit()
    pca.channels[PUMP_TARO].duty_cycle = 0
    pca.channels[PUMP_MATCHA].duty_cycle = 0
    pca.channels[PUMP_MILK].duty_cycle = 0
    pca.channels[STIRRER].duty_cycle = 0
    stirrer_servo.stop()
    claw_servo.stop()
    joint_servo1.stop()
    joint_servo2.stop()
    GPIO.cleanup()


