from gpiozero import OutputDevice
from time import sleep

# --- Pin Definitions ---
# Use the BCM GPIO pin numbers
PUMP1_PIN = 14 # Pump 1: Milk Tea
PUMP2_PIN = 15 # Pump 2: Matcha
PUMP3_PIN = 18 # Pump 3: Taro

# Initialize the pumps
pump1 = OutputDevice(PUMP1_PIN, active_high=True, initial_value=False)
pump2 = OutputDevice(PUMP2_PIN, active_high=True, initial_value=False)
pump3 = OutputDevice(PUMP3_PIN, active_high=True, initial_value=False)

# --- Calibration Settings ---
SECONDS_PER_OUNCE = 0.89
CUP_SIZE_OZ = 12.0

# --- Siphon Prevention Calibration ---
# Time (in seconds) it takes for the pump to push liquid from the reservoir 
# all the way to the tip of the nozzle before it actually starts dropping into the cup.
# You will need to time this with a stopwatch for your specific tube length.
PRIME_TIME_SECONDS = 1.5 

def pour_drink(pump, ounces):
    """Turns on the specified pump, accounting for tube priming."""
    # Total time = time to fill the empty tube + time to pour the actual drink
    pour_time = ounces * SECONDS_PER_OUNCE
    total_time = PRIME_TIME_SECONDS + pour_time
    
    print(f"--> Priming tube for {PRIME_TIME_SECONDS}s, then dispensing {ounces} oz...")
    
    pump.on()           # Turn pump ON
    sleep(total_time)   # Wait while the tube fills, then dispenses the drink
    pump.off()          # Turn pump OFF
    
    print("--> Pour complete! Gravity will now drain the tube back into the reservoir.\n")

def display_menu():
    """Runs the interactive text menu."""
    while True:
        print("==========================")
        print("    TEA DISPENSER MENU    ")
        print("==========================")
        print("1. Milk Tea")
        print("2. Matcha")
        print("3. Taro")
        print("4. Exit")
        print("==========================")
        
        # Wait for the user to type a choice
        choice = input("Enter the number of your drink (1-4): ")
        
        if choice == '1':
            print("\nPreparing a 12oz Milk Tea...")
            pour_drink(pump1, CUP_SIZE_OZ)
            
        elif choice == '2':
            print("\nPreparing a 12oz Matcha...")
            pour_drink(pump2, CUP_SIZE_OZ)
            
        elif choice == '3':
            print("\nPreparing a 12oz Taro...")
            pour_drink(pump3, CUP_SIZE_OZ)
            
        elif choice == '4':
            print("\nShutting down dispenser...")
            break # Exits the while loop
            
        else:
            print("\n[!] Invalid choice. Please enter a number between 1 and 4.\n")
        
        sleep(1) # Small pause before showing the menu again

if __name__ == "__main__":
    try:
        display_menu()
        
    except KeyboardInterrupt:
        print("\nForce quitting...")
        
    finally:
        pump1.off()
        pump2.off()
        pump3.off()