"""
Minimal I2S microphone test script.
"""
try:
    import sounddevice as sd
    import numpy as np
    import time
except ImportError as e:
    print(f"Missing Python dependencies: {e}")
    print("Please install the required packages:")
    print("For Raspberry Pi: sudo apt update && sudo apt install python3-pip libasound-dev")
    print("Then: pip3 install sounddevice numpy")
    exit(1)

def test_microphone():
    """Test basic microphone recording."""
    print("Testing I2S microphone...")
    
    # Test parameters
    sample_rate = 16000
    duration = 3.0  # seconds
    
    try:
        # List available devices
        print("Available audio devices:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  {i}: {device['name']} (input)")
        
        # Try to record
        print(f"\nRecording {duration}s of audio...")
        audio_data = sd.rec(
            int(sample_rate * duration),
            samplerate=sample_rate,
            channels=1,
            dtype=np.int16
        )
        sd.wait()
        print("Recording successful!")
        print(f"Captured {len(audio_data)} samples")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Common fixes:")
        print("1. Check the I2S overlay and wiring in SETUP_GUIDE.md.")
        print("   For the Adafruit SPH0645, use GPIO18/19/20.")
        print("2. Check that sounddevice lists an input device above.")
        print("3. Verify that the default input is the I2S microphone.")
        print("4. See SETUP_GUIDE.md for virtual-environment dependencies.")

if __name__ == "__main__":
    test_microphone()