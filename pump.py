import speech_recognition as sr
import RPi.GPIO as GPIO
import time
import pyttsx3

# --- Configuration ---
PUMP_MILK_TEA = 17
PUMP_MATCHA = 27
PUMP_TARO = 22

TUBE_PRIME_TIME = 2.0  
TARGET_VOLUME_TIME = 5.0 
TOTAL_PUMP_TIME = TUBE_PRIME_TIME + TARGET_VOLUME_TIME

# --- TTS Setup ---
engine = pyttsx3.init()
engine.setProperty('rate', 150) # Sets the speed of speech (default is usually ~200)

def speak(text):
    print(f"System: {text}")
    engine.say(text)
    engine.runAndWait()

# --- GPIO Setup ---
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for pin in [PUMP_MILK_TEA, PUMP_MATCHA, PUMP_TARO]:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH) 

def dispense_tea(tea_name, pin):
    speak(f"Coming right up! Dispensing your {tea_name}.")
    GPIO.output(pin, GPIO.LOW) # Turn pump ON
    
    time.sleep(TOTAL_PUMP_TIME) 
    
    GPIO.output(pin, GPIO.HIGH) # Turn pump OFF
    speak(f"Your {tea_name} is ready. Enjoy!")

def main():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Adjusting for background noise...")
        recognizer.adjust_for_ambient_noise(source)

    speak("The tea dispenser is ready. Would you like milk tea, matcha, or taro?")

    while True:
        try:
            with mic as source:
                # Listen for the user's response
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            
            command = recognizer.recognize_google(audio).lower()
            print(f"Heard: {command}")

            if "milk tea" in command:
                dispense_tea("Milk Tea", PUMP_MILK_TEA)
            elif "matcha" in command:
                dispense_tea("Matcha", PUMP_MATCHA)
            elif "taro" in command:
                dispense_tea("Taro", PUMP_TARO)
            else:
                speak("I didn't catch a tea name. Please say milk tea, matcha, or taro.")
                
        except sr.UnknownValueError:
            # Triggered if the mic picks up noise it can't translate to words
            speak("Sorry, I couldn't understand that. Please try again.")
        except sr.WaitTimeoutError:
            pass # No speech detected, loop continues silently
        except KeyboardInterrupt:
            speak("Shutting down the system. Goodbye.")
            break
        except Exception as e:
            print(f"Error: {e}")

    GPIO.cleanup()

if __name__ == "__main__":
    main()