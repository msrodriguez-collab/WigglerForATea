# I2S Microphone Not Detected - Troubleshooting Guide

## ⚠️ Important: Config File Location

**Newer Raspberry Pi OS (Pi 5, latest updates):** `/boot/firmware/config.txt`

**Older Raspberry Pi OS:** `/boot/config.txt`

Check which one you have:
```bash
ls -la /boot/config.txt /boot/firmware/config.txt
```

Use whichever file exists on your system in the following steps.

If `arecord -l` shows no devices, follow these steps in order:

### Step 1: Verify Device Tree Overlay is Loaded

```bash
# Check if I2S overlay is active
cat /proc/device-tree/overlays

# You should see:
# i2s
```

**If NOT found:** Overlay is not loaded. Go to Step 3.

**If found:** Overlay is loaded. Go to Step 2.

---

### Step 2: Check /proc/asound

```bash
# List ALSA devices
cat /proc/asound/devices
ls /proc/asound/

# Should show something like:
#  0: [ ]    : control
# 32: [ ]   : digital audio playback
# 33: [ ]   : digital audio capture
```

**If devices exist but not in `arecord -l`:** The kernel sees the device but it's not properly registered. Try rebooting: `sudo reboot`

**If NO devices in /proc/asound:** Go to Step 3.

---

### Step 3: Fix Device Tree Overlay Configuration

This is the most common issue.

#### 3a. Edit config.txt

For **newer OS** (Pi 5):
```bash
sudo nano /boot/firmware/config.txt
```

For **older OS**:
```bash
sudo nano /boot/config.txt
```

**Look for these lines near the bottom (or add them if missing):**

```ini
# Enable I2S
dtoverlay=i2s-gpio18-27-17-24
```

**Common configurations:**

```ini
# Option 1: Use specific GPIO pins (GPIO 18, 27, 17)
dtoverlay=i2s-gpio18-27-17-24

# Option 2: Use any available pins (let system choose)
dtoverlay=i2s-gpio

# Option 3: Older Raspberry Pi (if above doesn't work)
dtparam=i2s=on
```

#### 3b. Save and Reboot

- Press: `Ctrl+X`, then `Y`, then `Enter`
- Reboot: `sudo reboot`
- Wait for Pi to fully boot (1-2 minutes)

#### 3c. Verify Overlay Loaded

```bash
cat /proc/device-tree/overlays
# Should show: i2s
```

#### 3d. Check for Audio Devices

```bash
arecord -l
# Should now show your device
```

---

### Step 4: Verify Pin Connections

If overlay is loaded but still no devices, check physical connections.

**Required pins for `dtoverlay=i2s-gpio18-27-17-24`:**

| Signal | GPIO | Pin # | Microphone Pin |
|--------|------|-------|----------------|
| BCLK   | 18   | 12    | BCLK           |
| LRCLK  | 27   | 13    | LRCLK          |
| DOUT   | 17   | 11    | DOUT (or SD)   |
| GND    | -    | 6,9,14,20,25,30,34,39 | GND |
| VIN    | -    | 3.3V or 5V | VIN |

**Use a multimeter to check:**

1. **Voltage on VIN:** Should show 3.3V or 5V (depending on connection)
2. **Continuity on GND:** Should have 0Ω between microphone GND and RPi GND
3. **Check for shorts:** No continuity between signal lines and GND/VIN

**Raspberry Pi Pin Diagram:**
```
     +3.3V (1,17)  +5V (2,4)
GND (6,9,14,20,25,30,34,39)

GPIO 17 (Pin 11) <- DOUT (data output from microphone)
GPIO 18 (Pin 12) <- BCLK (bit clock)
GPIO 27 (Pin 13) <- LRCLK (left/right clock)
```

---

### Step 5: Verify Microphone is Powered

With a **multimeter in DC voltage mode**:

1. **Check VIN pin voltage:**
   - Probe: Positive → microphone VIN
   - Probe: Negative → microphone GND
   - **Expected:** 3.3V or 5V (depending on your connection)
   - **If 0V:** Power connection is broken

2. **Check continuity from RPi to microphone:**
   - Set multimeter to continuity/resistance mode
   - Probe GND on both devices
   - **Expected:** 0Ω (continuous connection)
   - **If ∞Ω:** Connection is broken

---

### Step 6: Check for GPIO Conflicts

Other device tree overlays might conflict with I2S.

For **newer OS**:
```bash
cat /boot/firmware/config.txt | grep dtoverlay
cat /boot/firmware/config.txt | grep dtparam
```

For **older OS**:
```bash
cat /boot/config.txt | grep dtoverlay
cat /boot/config.txt | grep dtparam
```

**Look for:**
- SPI overlay (uses GPIO 18, 27, 17)
- Other audio overlays
- Pin conflicts

**If conflicts found:**
- Comment out conflicting overlays with `#`
- Reboot
- Test again

---

### Step 7: Try Alternative Overlay

If `dtoverlay=i2s-gpio18-27-17-24` doesn't work:

For **newer OS**:
```bash
sudo nano /boot/firmware/config.txt
```

For **older OS**:
```bash
sudo nano /boot/config.txt
```

Replace with:
```ini
dtoverlay=i2s-gpio
```

This uses default I2S pins but may work better on some systems. Reboot and test.

---

### Step 8: Enable Verbose Kernel Logging

To see what's happening during boot:

For **newer OS**:
```bash
# Add to /boot/firmware/config.txt
dtdebug=1

# Then reboot and check dmesg
sudo reboot
dmesg | grep -i i2s
dmesg | grep -i overlay
```

For **older OS**:
```bash
# Add to /boot/config.txt
dtdebug=1

# Then reboot and check dmesg
sudo reboot
dmesg | grep -i i2s
dmesg | grep -i overlay
```

Look for error messages about I2S or GPIO pins.

---

### Step 9: Run Diagnostic Script

Copy the diagnostic script to your Pi and run it:

```bash
# On your Pi:
bash i2s_diagnostics.sh

# This will show:
# - Whether overlay is loaded
# - Available audio devices
# - GPIO status
# - System log messages
# - Recommendations
```

---

## Advanced Troubleshooting

### Check Kernel Messages

```bash
# See ALL kernel messages related to I2S
dmesg | grep -E "i2s|audio|bcm2835" | head -20

# Look for errors like:
# "i2s-gpio: probe failed"
# "gpio-request: unable to request GPIO"
# "Cannot allocate DMA"
```

### Manually Test GPIO Pins

```bash
# List GPIO information
sudo apt-get install gpiod
gpioinfo gpiochip0 | grep -E "17|18|27"

# Should show the pins exist and are not in use
```

### Test with Direct ALSA

```bash
# List devices in detail
aplay -l
arecord -l

# Test recording with specific device
arecord -D hw:1,0 -f S16_LE -r 16000 -c 1 -d 5 test.wav
```

### Rebuild Device Tree

Sometimes the device tree needs to be rebuilt:

```bash
cd /boot
sudo dtc -I dts -O dtb overlays/i2s-gpio18-27-17-24.dts -o i2s-gpio18-27-17-24.dtbo
sudo reboot
```

---

## If Still Not Working

At this point, collect this information and seek help:

For **newer OS** (/boot/firmware/config.txt):
```bash
# Create a diagnostic file
{
  echo "=== Raspberry Pi Model ==="
  cat /proc/device-tree/model
  echo ""
  echo "=== Kernel Version ==="
  uname -r
  echo ""
  echo "=== /boot/firmware/config.txt (I2S section) ==="
  grep -A5 -B5 "i2s" /boot/firmware/config.txt
  echo ""
  echo "=== Device Tree Overlays ==="
  ls -la /proc/device-tree/overlays/
  echo ""
  echo "=== ALSA Devices ==="
  arecord -l
  echo ""
  echo "=== /proc/asound ==="
  cat /proc/asound/devices
  echo ""
  echo "=== dmesg (last 50 lines) ==="
  dmesg | tail -50
} > diagnostic_report.txt

# Send this file for analysis
cat diagnostic_report.txt
```

For **older OS** (/boot/config.txt):
```bash
# Create a diagnostic file
{
  echo "=== Raspberry Pi Model ==="
  cat /proc/device-tree/model
  echo ""
  echo "=== Kernel Version ==="
  uname -r
  echo ""
  echo "=== /boot/config.txt (I2S section) ==="
  grep -A5 -B5 "i2s" /boot/config.txt
  echo ""
  echo "=== Device Tree Overlays ==="
  ls -la /proc/device-tree/overlays/
  echo ""
  echo "=== ALSA Devices ==="
  arecord -l
  echo ""
  echo "=== /proc/asound ==="
  cat /proc/asound/devices
  echo ""
  echo "=== dmesg (last 50 lines) ==="
  dmesg | tail -50
} > diagnostic_report.txt

# Send this file for analysis
cat diagnostic_report.txt
```

---

## Common Solutions Summary

| Issue | Solution |
|-------|----------|
| No devices in `arecord -l` | Add `dtoverlay=i2s-gpio18-27-17-24` to /boot/config.txt, reboot |
| Overlay won't load | Check /boot/config.txt syntax, ensure no GPIO conflicts |
| Overlay loads but no audio | Check pin connections, verify microphone power |
| ALSA sees device but can't record | Check GPIO pin assignments, try different overlay |
| High noise/distortion | Check grounding, use shielded cables, reduce sample rate |
| Permission denied errors | Add user to `audio` group: `sudo usermod -a -G audio $USER` |

---

## References

- [Raspberry Pi I2S Configuration](https://www.raspberrypi.com/documentation/computers/configuration.html#audio)
- [Device Tree Overlays Documentation](https://github.com/raspberrypi/linux/tree/rpi-6.1.y/arch/arm/boot/dts/overlays)
- [ALSA Capture Devices](https://wiki.debian.org/ALSA#Recording)
- [Adafruit I2S MEMS Microphone](https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout)
