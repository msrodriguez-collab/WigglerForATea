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
        print("1. Ensure I2S overlay is configured in /boot/config.txt")
        print("   Add: dtoverlay=i2s-gpio18-27-17-24")
        print("2. Install required packages:")
        print("   sudo apt update && sudo apt install libasound-dev python3-pip")
        print("   pip3 install sounddevice numpy")
        print("3. Check that the microphone is properly connected")
        print("4. Verify the I2S GPIO pin configuration matches your hardware")

if __name__ == "__main__":
    test_microphone()