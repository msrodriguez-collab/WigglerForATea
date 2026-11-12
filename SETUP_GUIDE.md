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

### 1. Enable I2S Interface
```bash
sudo raspi-config
# Navigate to: Interfacing Options → I2C/SPI → I2S
# Select Enable, then reboot
```

### 2. Update System Packages
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 3. Install System Dependencies
```bash
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    libatlas-base-dev \
    libjasper-dev \
    libtiff5 \
    libjasper1 \
    libharfbuzz0b \
    libwebp6 \
    libtiff5 \
    libopenjp2-7 \
    libtiffxx5
```

### 4. Install Adafruit Libraries
```bash
pip3 install --upgrade adafruit-python-shell
pip3 install adafruit-circuitpython-bus
pip3 install adafruit-circuitpython-i2sout
pip3 install adafruit-circuitpython-i2sin
```

### 5. Install Audio Processing Libraries
```bash
pip3 install numpy soundfile scipy
```

## Speech-to-Text Backend Options

### Option A: Google Cloud Speech-to-Text (Recommended for High Accuracy)

**Pros:**
- Excellent accuracy
- Multiple language support
- Real-time streaming support

**Setup:**
```bash
pip3 install google-cloud-speech
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

**Setup:**
```bash
pip3 install openai
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

**Setup:**
```bash
pip3 install vosk pocketsphinx
```

## Usage

### Basic Recording Example
```python
from recordingsound import I2SMicrophoneRecorder, SpeechToTextConverter

# Record 5 seconds of audio
recorder = I2SMicrophoneRecorder(sample_rate=16000)
audio_data, sample_rate = recorder.record(5.0, "output.wav")
recorder.close()

# Transcribe using your chosen backend
transcriber = SpeechToTextConverter(backend="google")  # or "openai" or "vosk"
text = transcriber.transcribe("output.wav")
print(f"Transcribed text: {text}")
```

### Complete Pipeline
```python
from recordingsound import I2SMicrophoneRecorder, SpeechToTextConverter
from datetime import datetime

# Initialize recorder
recorder = I2SMicrophoneRecorder(sample_rate=16000)

# Record audio
filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
audio_data, sr = recorder.record(duration_seconds=10.0, output_file=filename)
recorder.close()

# Transcribe
transcriber = SpeechToTextConverter(backend="google")
result = transcriber.transcribe(filename)
print(f"Result: {result}")
```

## Troubleshooting

### I2S Device Not Found
- Verify I2S is enabled: `sudo raspi-config` → Interfacing Options → I2S
- Check pin connections with multimeter
- Try `gpio readall` to verify GPIO functionality

### Audio Recording Issues
- Check microphone orientation (DOUT should be data output)
- Verify microphone has power (check with voltmeter)
- Try different sample rates (8000, 16000, 48000 Hz)

### Speech Recognition Not Working
- Ensure audio file has speech (check with `ffplay` or `aplay`)
- Verify API credentials are correctly set
- Check internet connection for cloud backends

### High CPU Usage
- Reduce sample rate
- Use shorter recording durations
- Use Vosk for offline processing

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
