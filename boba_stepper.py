import speech_recognition as sr
import pyttsx3
import RPi.GPIO as GPIO
import time

# --- Configuration for NEMA 17 Stepper Motor ---
DIR_PIN = 20
STEP_PIN = 21
STEPS_PER_REV = 200
STEP_DELAY = 0.005 

BOBA_LEVELS = {
    "no boba": 0,
    "low boba": STEPS_PER_REV * 2,  
    "mid boba": STEPS_PER_REV * 4,  
    "big boba": STEPS_PER_REV * 6   
}

# --- TTS and GPIO Setup ---
engine = pyttsx3.init()
engine.setProperty('rate', 150)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STEP_PIN, GPIO.OUT)

def speak(text):
    """Outputs speech through the connected speaker."""
    print(f"System: {text}")
    engine.say(text)
    engine.runAndWait()

def dispense_boba(level):
    """Rotates the NEMA 17 stepper motor to dispense the requested boba."""
    steps = BOBA_LEVELS.get(level)
    
    if steps == 0:
        speak("Skipping boba.")
        return

    speak(f"Dispensing {level}.")
    GPIO.output(DIR_PIN, GPIO.HIGH)
    
    for _ in range(steps):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(STEP_DELAY)
        
    speak("The tea is ready!")

def main():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Adjusting for background noise...")
        recognizer.adjust_for_ambient_noise(source)

    speak("The boba dispenser is ready. Would you like no boba, low boba, mid boba, or big boba?")

    while True:
        try:
            with mic as source:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
            
            command = recognizer.recognize_google(audio).lower()
            print(f"Heard: {command}")

            if "no boba" in command:
                dispense_boba("no boba")
            elif "low boba" in command:
                dispense_boba("low boba")
            elif "mid boba" in command:
                dispense_boba("mid boba")
            elif "big boba" in command:
                dispense_boba("big boba")
            else:
                speak("I didn't catch that size. Please say no boba, low boba, mid boba, or big boba.")
                
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand that. Please try again.")
        except sr.WaitTimeoutError:
            pass # Loop continues silently if no speech is detected
        except KeyboardInterrupt:
            speak("Shutting down the boba dispenser. Goodbye.")
            break
        except Exception as e:
            print(f"Error: {e}")

    GPIO.cleanup()

if __name__ == "__main__":
    main()