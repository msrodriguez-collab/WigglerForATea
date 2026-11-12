"""
Minimal I2S microphone test script.
"""
import sounddevice as sd
import numpy as np
import time

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
        print("2. Run 'sudo apt update && sudo apt install libasound-dev'")
        print("3. Check that the microphone is properly connected")
        print("4. Try running with sudo")

if __name__ == "__main__":
    test_microphone()