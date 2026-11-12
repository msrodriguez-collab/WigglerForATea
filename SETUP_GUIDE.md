# Raspberry Pi I2S Microphone and Speech-to-Text Setup

This guide covers the Adafruit SPH0645 I2S MEMS microphone breakout and
Raspberry Pi OS. Other microphone breakouts may have different pin labels or
requirements; check their documentation before wiring.

The earlier version of this guide gave incorrect GPIO and overlay instructions.
Do not use the older `I2S_TROUBLESHOOTING.md` or `i2s_diagnostics.sh`: they
still contain those incorrect instructions.

## 1. Wire the microphone

Shut down the Pi and disconnect its power before connecting or moving wires.
For the SPH0645 breakout, use these connections:

| Microphone pin | Raspberry Pi connection |
| --- | --- |
| 3V | 3.3V, physical pin 1 |
| GND | Ground, physical pin 6 |
| BCLK | GPIO18, physical pin 12 |
| LRCL / LRCLK | GPIO19, physical pin 35 |
| DOUT | GPIO20, physical pin 38 |
| SEL | Ground, for the left channel |

These are BCM GPIO numbers, not physical pin numbers. The microphone's DOUT
connects to the Pi's I2S **input**, not its output. See the
[Adafruit wiring guide](https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout/raspberry-pi-wiring-test)
for a diagram.

## 2. Configure the sound card

On the Pi, edit the boot configuration:

```bash
sudo nano /boot/firmware/config.txt
```

On older Raspberry Pi OS installations the active file may instead be
`/boot/config.txt`. Use the active configuration file for your installation.

If you followed the previous guide, comment out the lines it suggested by
putting `#` in front of them:

```ini
#dtoverlay=i2s-gpio
#dtoverlay=i2s-gpio18-27-17-24
```

Leave unrelated configuration alone. Under an existing `[all]` section, or in
a new `[all]` section at the end of the file, add:

```ini
[all]
dtoverlay=googlevoicehat-soundcard
```

Avoid adding a duplicate if the overlay is already enabled. Save with
Ctrl+X, Y, Enter, then reboot:

```bash
sudo reboot
```

The overlay configures a sound card; the microphone itself is not a
plug-and-play device. A listed card alone does not prove that the microphone is
connected or recording correctly.

## 3. Check and test recording

Install the ALSA utilities if needed:

```bash
sudo apt update
sudo apt install alsa-utils
arecord -l
```

Look for a capture card named something like `voicehat`. Note its card and
device numbers. If `arecord` reports no capture hardware, see Troubleshooting
below; do not assume card 1 is correct.

With the card number and device number from `arecord -l`, record a test. For
example, if it lists **card 1, device 0**, run:

```bash
arecord -D plughw:1,0 -c 1 -r 48000 -f S32_LE -t wav -d 5 -V mono -v test.wav
aplay test.wav
```

Replace `1,0` with your own card and device numbers. Speak while recording and
listen through a configured playback device, or copy the WAV file to another
computer. Adafruit notes that this overlay uses a fixed 48 kHz hardware rate;
`plughw` permits ALSA to perform format conversion when needed. If the file
is silent, check wiring and the SEL channel before trying speech recognition.

## 4. Set up Python

Modern Raspberry Pi OS protects its system Python environment. Install project
packages in a virtual environment instead of using `sudo pip` or
`--break-system-packages`:

```bash
sudo apt update
sudo apt install python3-venv python3-pip libportaudio2 libsndfile1
cd "/path/to/your/Final Project"
python3 -m venv env
source env/bin/activate
python -m pip install -r requirements.txt
```

Replace the example path with the actual project directory. Activate the
environment again in each new terminal with `source env/bin/activate`.
`requirements.txt` does not install a speech recognition backend by default.
The CircuitPython I2S packages previously listed are not needed for this ALSA
recording workflow.

## 5. Transcribe the test recording offline

This example uses Vosk and SoX. It downloads an English model once; recognition
then runs locally. Vosk package availability depends on the Pi's architecture
and Python version.

```bash
sudo apt install sox unzip wget
source env/bin/activate
python -m pip install vosk
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

Convert the test recording to the mono, 16-bit, 16 kHz WAV format expected by
this example:

```bash
sox test.wav -c 1 -b 16 -e signed-integer speech.wav rate 16000
```

From the same directory, run:

```bash
python - <<'PY'
import json
import wave
from vosk import Model, KaldiRecognizer

model = Model("vosk-model-small-en-us-0.15")
with wave.open("speech.wav", "rb") as audio:
    if (audio.getnchannels(), audio.getsampwidth(), audio.getframerate()) != (1, 2, 16000):
        raise ValueError("Expected mono, 16-bit, 16 kHz WAV audio")
    recognizer = KaldiRecognizer(model, audio.getframerate())
    segments = []
    while True:
        data = audio.readframes(4000)
        if not data:
            break
        if recognizer.AcceptWaveform(data):
            segments.append(json.loads(recognizer.Result())["text"])
    segments.append(json.loads(recognizer.FinalResult())["text"])
    print("Transcript:", " ".join(segment for segment in segments if segment))
PY
```

An empty transcript can mean that no speech was recognized. Listen to the test
recording first and try again in a quiet environment. Models for other
languages are listed on the [Vosk models page](https://alphacephei.com/vosk/models).

### Existing Python script

`recordingsound.py` is an earlier experiment, not the tested workflow above.
Its hardware comments and device auto-detection are unreliable, and its Vosk
and cloud transcription paths need correction. In particular, an ALSA card
number from `arecord -l` is not necessarily a `sounddevice` device index.
Use the ALSA and Vosk steps above until the script has been updated and tested.

## Troubleshooting

- **No capture card:** Confirm that the correct config file contains an
  uncommented `dtoverlay=googlevoicehat-soundcard` in an applicable section,
  reboot, and run `arecord -l` again. Check available overlays with
  `ls /boot/firmware/overlays/googlevoicehat-soundcard.dtbo`. The overlay may
  be missing on some installations. Other sound overlays or GPIO use can
  conflict; investigate before changing unrelated settings.
- **Missing `/proc/device-tree/overlays`:** Its absence does not prove a
  boot-time overlay failed to load. Do not use it as an overlay success test.
- **Card appears but audio is silent:** Power down before checking the
  connections, including SEL to ground. Verify the microphone is powered and
  that you selected its capture card rather than a playback device.
- **`arecord` fails:** Check the reported card and device numbers and use the
  `plughw` command above. Check the exact error before changing formats.
- **Python installation fails:** Ensure the virtual environment is active and
  use `python -m pip`. For a “no matching distribution” error, note the
  package name, Python version (`python --version`), and architecture
  (`uname -m`); compatibility varies by package and platform. System packages
  installed with `apt` are not normally visible inside a default venv.
- **Still stuck:** Collect `cat /proc/device-tree/model`, `cat /etc/os-release`,
  `arecord -l`, and the relevant uncommented overlay lines from the active
  config file. Avoid sharing unrelated private configuration.

## References

- [Adafruit SPH0645 Raspberry Pi wiring and test](https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout/raspberry-pi-wiring-test)
- [Raspberry Pi configuration documentation](https://www.raspberrypi.com/documentation/computers/config_txt.html)
- [Vosk speech recognition](https://alphacephei.com/vosk/)
