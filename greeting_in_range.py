import RPi.GPIO as GPIO
import time
import pyttsx3

# --- Configuration ---
TRIG_PIN = 23
ECHO_PIN = 24
DISTANCE_THRESHOLD_CM = 100  # 1 meter
MEASUREMENT_INTERVAL = 5.0   # seconds

# --- TTS Setup ---
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    """Outputs speech through the connected USB speaker."""
    print(f"System: {text}")
    engine.say(text)
    engine.runAndWait()

# --- GPIO Setup ---
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

def get_distance():
    """Triggers the HC-SR04 and calculates distance in centimeters."""
    # Ensure TRIG is low
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.01)

    # Send a 10 microsecond pulse to trigger
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    pulse_start = time.time()
    pulse_end = time.time()

    # Wait for the ECHO pin to go high
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()

    # Wait for the ECHO pin to go low
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    # Calculate pulse duration and convert to distance (speed of sound = 343m/s)
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

def main():
    speak("Range finder initialized and waiting for customers.")
    
    try:
        while True:
            dist = get_distance()
            print(f"Measured Distance: {dist} cm")
            
            if dist < DISTANCE_THRESHOLD_CM:
                speak("Hello! Welcome to the tea dispenser. Would you like milk tea, matcha, or taro?")
                
            time.sleep(MEASUREMENT_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nShutting down proximity sensor.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()