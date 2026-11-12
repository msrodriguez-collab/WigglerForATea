# Raspberry Pi I2S MEMS Microphone Audio Recording & Speech-to-Text Setup Guide

## Hardware Requirements

- **Raspberry Pi** (4B or newer recommended)
- **Adafruit I2S MEMS Microphone Breakout** (SPH0645 or similar)
- **MicroSD Card** (at least 16GB)
- **Power Supply** (5V for RPi, proper USB-C or barrel connector)
- **Jumper Wires** (for GPIO connections)

## Pin Connections

Connect the Adafruit I2S MEMS microphone to your Raspberry Pi:

```
Microphone Pin   →  Raspberry Pi Pin
VIN              →  5V (Pin 2 or 4) or 3.3V (Pin 1 or 17)
GND              →  GND (Pin 6, 9, 14, 20, 25, 30, 34, or 39)
BCLK             →  GPIO 18 (Pin 12)
LRCLK            →  GPIO 27 (Pin 13)
DOUT             →  GPIO 17 (Pin 11)
```

**Note:** Verify your breakout's pinout diagram before connecting. Some variants may differ.

## Initial Raspberry Pi Setup

### 1. Enable I2S Interface and Configure Device Tree Overlay

```bash
# Edit boot config
sudo nano /boot/config.txt

# Add these lines at the end:
dtoverlay=i2s-gpio
# For specific GPIO pins (GPIO 18, 27, 17):
dtoverlay=i2s-gpio18-27-17-24

# Save and exit (Ctrl+X, Y, Enter)
```

After editing, reboot:
```bash
sudo reboot
```

### 2. Verify I2S Device Registration

After reboot, check that the I2S device is recognized:

```bash
# List audio recording devices
arecord -l

# You should see output like:
# **** List of CAPTURE Hardware Devices ****
# card 1: i2smic [i2smic], device 0: bcm2835_i2smic-hifiberry-dac-adda snd_rpi_hifiberry_dac_adda_hw:0 []

# Also check with ALSA controls
alsamixer

# Test recording (10 seconds):
arecord -D hw:1,0 -f S16_LE -r 16000 -c 1 -d 10 test_recording.wav
```

### 3. Update System Packages
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 4. Install System Dependencies
```bash
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    libasound2-dev \
    portaudio19-dev \
    libatlas-base-dev \
    libjasper-dev \
    libtiff5 \
    libjasper1 \
    libharfbuzz0b \
    libwebp6 \
    libtiffxx5
```

### 4. Create and Activate Python Virtual Environment (IMPORTANT)

Due to PEP 668, modern Python installations prevent direct package installation. Use a virtual environment:

```bash
# Navigate to your project directory
cd /path/to/your/Final\ Project

# Create virtual environment
python3 -m venv env

# Activate it
source env/bin/activate

# Verify activation (you should see (env) in your terminal prompt)
```

### 5. Install All Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements at once
pip install -r requirements.txt
```

**Or install individually:**
```bash
pip install --upgrade adafruit-python-shell
pip install adafruit-circuitpython-bus
pip install adafruit-circuitpython-i2sout
pip install adafruit-circuitpython-i2sin
pip install numpy soundfile scipy
```

### 6. Install Speech-to-Text Backend (Choose One)

After activating virtual environment:

```bash
# Google Cloud Speech-to-Text
pip install google-cloud-speech

# OR OpenAI Whisper
pip install openai

# OR Vosk (offline)
pip install vosk pocketsphinx
```

## Speech-to-Text Backend Options

### Option A: Google Cloud Speech-to-Text (Recommended for High Accuracy)

**Pros:**
- Excellent accuracy
- Multiple language support
- Real-time streaming support

**Setup (with virtual environment activated):**
```bash
pip install google-cloud-speech
```

**Authentication:**
1. Create a Google Cloud project
2. Enable Speech-to-Text API
3. Create a service account and download JSON key
4. Set environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/key.json"
```

### Option B: OpenAI Whisper (Cloud-Based)

**Pros:**
- Very high accuracy
- Supports 99+ languages
- Straightforward API

**Setup (with virtual environment activated):**
```bash
pip install openai
```

**Configuration:**
1. Get OpenAI API key from https://platform.openai.com/api-keys
2. Set environment variable:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Option C: Vosk (Offline, No API Key)

**Pros:**
- Works offline (no internet required)
- No API key needed
- Faster for real-time processing

**Cons:**
- Lower accuracy than cloud solutions
- English and several other languages only

**Setup (with virtual environment activated):**
```bash
pip install vosk pocketsphinx
```

## Usage

### Important: Activate Virtual Environment First

Every time you open a new terminal on your Raspberry Pi:

```bash
cd /path/to/your/Final\ Project
source env/bin/activate  # You should see (env) in your prompt
```

### Basic Recording Example
```python
from recordingsound import I2SMicrophoneRecorder, SpeechToTextConverter

# Record 5 seconds of audio (auto-detects I2S device)
recorder = I2SMicrophoneRecorder(sample_rate=16000)
audio_data, sample_rate = recorder.record(5.0, "output.wav")

# If auto-detection fails, specify device manually:
# recorder = I2SMicrophoneRecorder(sample_rate=16000, device=1)

# Transcribe using your chosen backend
transcriber = SpeechToTextConverter(backend="vosk")  # or "google" or "openai"
text = transcriber.transcribe("output.wav")
print(f"Transcribed text: {text}")
```

### Complete Pipeline
```python
from recordingsound import I2SMicrophoneRecorder, SpeechToTextConverter
from datetime import datetime

# Initialize recorder (auto-detects I2S device)
recorder = I2SMicrophoneRecorder(sample_rate=16000)

# Record audio
filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
audio_data, sr = recorder.record(duration_seconds=10.0, output_file=filename)

# Transcribe
transcriber = SpeechToTextConverter(backend="vosk")
result = transcriber.transcribe(filename)
print(f"Result: {result}")
```

### Running Your Script

```bash
# Make sure virtual environment is activated first!
source env/bin/activate

# Run the main script
python3 recordingsound.py

# Or run your own script
python3 my_script.py
```

### Troubleshooting Recording

If recording fails, manually check your I2S device:

```bash
# List all audio devices
arecord -l

# Test recording directly (10 seconds, mono, 16kHz):
arecord -D hw:1,0 -f S16_LE -r 16000 -c 1 -d 10 test.wav
aplay test.wav

# Play the test file back to verify it recorded
```

Then update your code with the correct device number:
```python
recorder = I2SMicrophoneRecorder(sample_rate=16000, device=1)
```

## Troubleshooting

### I2S Device Not Found / Recording Fails
```bash
# Step 1: Verify device tree overlay is loaded
cat /proc/device-tree/overlays

# Step 2: List available audio devices
arecord -l

# Step 3: Test ALSA recording directly
arecord -D hw:1,0 -f S16_LE -r 16000 -c 1 -d 5 test.wav

# Step 4: Check GPIO connections with multimeter
# BCLK should be GPIO 18
# LRCLK should be GPIO 27  
# DOUT should be GPIO 17
# GND and VIN should be connected

# Step 5: If still failing, check dtoverlay configuration
cat /boot/config.txt | grep dtoverlay
```

### Installation Errors

**"No matching distribution found"** for sounddevice:
```bash
# Make sure you're in the virtual environment
source env/bin/activate

# Try installing with specific version
pip install sounddevice==0.4.5

# Or install from apt if pip fails
sudo apt-get install python3-sounddevice
```

**"ModuleNotFoundError" after installation:**
- Verify virtual environment is activated: `which python3` should show `env/bin/python3`
- Reinstall: `pip install --force-reinstall -r requirements.txt`

### Audio Recording Issues
- Check microphone orientation (DOUT should be data output)
- Verify microphone has power (check with voltmeter)
- Try different sample rates (8000, 16000, 48000 Hz)
- Test with: `arecord -D hw:1,0 -f S16_LE -r 16000 test.wav`

### Speech Recognition Not Working
- Ensure audio file has audible speech (test with `aplay`)
- Verify API credentials are correctly set for cloud backends
- Check internet connection for cloud services
- For Vosk: verify the model is installed correctly

### High CPU Usage
- Reduce sample rate (try 8000 Hz)
- Use shorter recording durations
- Use Vosk for offline processing
- Run on Raspberry Pi 4B+ (4 cores recommended)

## Performance Tips

1. **Use 16kHz sample rate** - Good balance between quality and processing speed
2. **Record in quiet environments** - Reduces processing overhead
3. **Use mono (1 channel)** - Stereo doubles data size
4. **Run on Raspberry Pi 4B+** - Dual-core is minimum, 4-core recommended
5. **Consider USB audio adapter** - Better noise isolation than onboard audio

## File Structure
```
Final Project/
├── recordingsound.py          # Main recording and transcription code
├── requirements.txt           # Python dependencies
├── SETUP_GUIDE.md            # This file
├── README.md                 # Project overview
└── recordings/               # Saved audio files (create this folder)
    └── recording_*.wav
```

## Next Steps

1. Test microphone connection with GPIO multimeter
2. Install all dependencies from requirements.txt
3. Run the main script with test recording
4. Adjust audio settings (sample rate, duration) as needed
5. Deploy your application

## References

- [Adafruit I2S MEMS Microphone Guide](https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout)
- [Raspberry Pi I2S Documentation](https://www.raspberrypi.com/documentation/computers/configuration.html#configuring-i2s)
- [Google Cloud Speech-to-Text API](https://cloud.google.com/speech-to-text/docs)
- [OpenAI Whisper API](https://platform.openai.com/docs/api-reference/audio/create-transcription)
- [Vosk Offline Speech Recognition](https://alphacephei.com/vosk/)
