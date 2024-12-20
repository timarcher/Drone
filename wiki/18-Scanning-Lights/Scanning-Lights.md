This page contains details on how I added an WS2812B LED light strip and connected it to the Raspberry Pi to create a Cylon light effect on the face of the drone.

# YouTube Video
- [Hexacopter Drone Build Project – Part 18 Cylon Lights](https://youtu.be/XXX)

# Notes
- Connect the 5v wire from the LED light strip to the 5v supply coming from the BEC. Also connect the ground wire to the 5v BEC, AND connect it to the ground pin on the raspberry pi. (The device needs a common ground for good data transfers.)
- Connect the data line from the LED light strip to GPIO10 (MOSI) on the raspberry pi. Put a 330 ohm resistor in series between the LED light strip and the Raspberry Pi GPIO pin.
- NeoPixels must be connected to GPIO10, GPIO12, GPIO18 or GPIO21 to work! GPIO18 is the standard pin.
- Sound must be disabled to use GPIO18. This can be done in /boot/firmware/config.txt by changing "dtparam=audio=on" to "dtparam=audio=off" and rebooting.
- Create a python environment and install the [Pi5Neo library](https://pypi.org/project/Pi5Neo/).
```sh
sudo apt update
sudo apt install python3-pip

python3 -m venv cylon_leds
source cylon_leds/bin/activate

pip3 install pi5neo
```

- Write a script to control the LEDs. Make a file named led_test.py and put the following in it:
```sh
from pi5neo import Pi5Neo

# Initialize the Pi5Neo class with 10 LEDs and an SPI speed of 800kHz
neo = Pi5Neo('/dev/spidev0.0', 20, 800)

# Fill the strip with a red color
neo.fill_strip(255, 0, 0)
neo.update_strip()  # Commit changes to the LEDs

# Set the 5th LED to blue
neo.set_led_color(4, 0, 0, 255)
neo.update_strip()   
```

- Run the script
```sh
python3 led_test.py
```

- Deactive and remove the virtual environment (optional):
```sh
deactivate
rm -rf cylon_leds
```


# Sample Scripts
- [This script](../../src/sample03_neopixel_examples/cylon_scan.py) will make a scanning LED pattern where the strip is lit up in red, and 7 LEDs will "scan" back and forth in a blue color.
- [This script](../../src/sample03_neopixel_examples/cylon_scan_dual_end.py) will make a scanning LED pattern where the strip is lit up in red, and the scanning LEDs start at each end of the strip, move toward the center, and then reverse direction back to each end.


# Supporting Materials
- [ArduPilot Configuration](../ArduPilot-Config/ArduPilot-Config.md) - This page contains a consolidated list of the all of the configuration done in ArduPilot throughout the videos.


# References 
- 