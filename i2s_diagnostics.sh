#!/bin/bash
# I2S Microphone Diagnostic Script for Raspberry Pi
# Run with: bash i2s_diagnostics.sh

echo "=========================================="
echo "I2S Microphone Diagnostic Script"
echo "=========================================="
echo ""

# Step 1: Check if running on Raspberry Pi
echo "Step 1: Checking Raspberry Pi Model..."
if [ -f /proc/device-tree/model ]; then
    echo "✓ $(cat /proc/device-tree/model)"
else
    echo "✗ Not running on Raspberry Pi or cannot read model"
    exit 1
fi
echo ""

# Step 2: Check /boot/config.txt for I2S configuration
echo "Step 2: Checking config.txt..."
if [ -f /boot/firmware/config.txt ]; then
    CONFIG_FILE="/boot/firmware/config.txt"
    echo "✓ Using /boot/firmware/config.txt (Raspberry Pi 5 / newer OS)"
elif [ -f /boot/config.txt ]; then
    CONFIG_FILE="/boot/config.txt"
    echo "✓ Using /boot/config.txt (older OS)"
else
    echo "✗ Cannot find config.txt!"
    exit 1
fi

if grep -q "dtoverlay=i2s" "$CONFIG_FILE"; then
    echo "✓ I2S overlay found in config.txt:"
    grep "dtoverlay=i2s" "$CONFIG_FILE"
else
    echo "✗ No I2S overlay found"
    echo "  Add this line to $CONFIG_FILE:"
    echo "  dtoverlay=i2s-gpio18-27-17-24"
fi
echo ""

# Step 3: Check loaded device tree overlays
echo "Step 3: Checking loaded device tree overlays..."
if [ -d /proc/device-tree/overlays ]; then
    echo "Available overlays:"
    ls -1 /proc/device-tree/overlays/
    if [ -d /proc/device-tree/overlays/i2s ]; then
        echo "✓ I2S overlay is loaded"
    else
        echo "✗ I2S overlay NOT loaded (reboot required after /boot/config.txt changes)"
    fi
else
    echo "✗ Cannot access device tree overlays"
fi
echo ""

# Step 4: Check GPIO permissions
echo "Step 4: Checking GPIO access..."
if [ -d /sys/class/gpio ]; then
    echo "✓ GPIO interface is available"
else
    echo "✗ GPIO interface not available"
fi
echo ""

# Step 5: Check ALSA devices
echo "Step 5: Checking ALSA audio devices..."
echo "Available recording devices:"
arecord -l
echo ""

# Step 6: Check /proc/asound
echo "Step 6: Checking /proc/asound..."
if [ -f /proc/asound/devices ]; then
    echo "ALSA devices:"
    cat /proc/asound/devices
else
    echo "✗ /proc/asound/devices not found"
fi
echo ""

# Step 7: Check dmesg for I2S errors
echo "Step 7: Checking system logs for I2S errors (last 30 lines)..."
dmesg | tail -30 | grep -i "i2s\|bcm2835\|audio\|mic" || echo "No I2S-related messages found"
echo ""

# Step 8: Test GPIO pins
echo "Step 8: GPIO Pin Status"
echo "Checking GPIO access (requires gpio utility or gpiod)..."
if command -v gpioinfo &> /dev/null; then
    echo "GPIO 17 (DOUT):"
    gpioinfo gpiochip0 17 2>/dev/null || echo "Cannot read GPIO 17"
    echo "GPIO 18 (BCLK):"
    gpioinfo gpiochip0 18 2>/dev/null || echo "Cannot read GPIO 18"
    echo "GPIO 27 (LRCLK):"
    gpioinfo gpiochip0 27 2>/dev/null || echo "Cannot read GPIO 27"
else
    echo "gpio utility not installed. Install with: sudo apt-get install gpiod"
fi
echo ""

# Step 9: Check if audio devices exist
echo "Step 9: Checking audio device files..."
ls -la /dev/snd/ 2>/dev/null || echo "No audio devices found in /dev/snd/"
echo ""

# Step 10: Recommendations
echo "=========================================="
echo "NEXT STEPS:"
echo "=========================================="
echo ""
echo "If I2S overlay is NOT loaded:"
echo "  1. Edit config.txt:       sudo nano \$CONFIG_FILE"
echo "  2. Add this line:         dtoverlay=i2s-gpio18-27-17-24"
echo "  3. Save and exit:         Ctrl+X, Y, Enter"
echo "  4. Reboot:                sudo reboot"
echo ""
echo "If I2S overlay IS loaded but no devices found:"
echo "  1. Check physical connections:"
echo "     - GPIO 18 (BCLK) - Pin 12"
echo "     - GPIO 27 (LRCLK) - Pin 13"
echo "     - GPIO 17 (DOUT) - Pin 11"
echo "     - GND - Any GND pin"
echo "     - VIN - 3.3V or 5V (check microphone specs)"
echo ""
echo "  2. Verify microphone has power (voltmeter test)"
echo ""
echo "  3. Try alternative device tree overlay:"
echo "     dtoverlay=i2s-gpio"
echo ""
echo "  4. Check for GPIO conflicts in \$CONFIG_FILE"
echo ""
echo "If still not working:"
echo "  1. Check dmesg output above for errors"
echo "  2. Verify Raspberry Pi SoC supports I2S (all models do)"
echo "  3. Try different GPIO pins if available"
echo ""
