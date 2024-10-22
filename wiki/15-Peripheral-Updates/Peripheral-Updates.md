This page contains details on various updates made to the drone.

# YouTube Video
- [Hexacopter Drone Build Project – Part 15 Peripheral Updates](https://youtu.be/XXX)

# Notes
At this stage, I did a bunch of little modifications and cleanup to the overall hardware of the drone including:
- Added a second Here4 GPS to the drone.
- Designed and printed a new top lid for the drone. The STL and Autodesk Fusion files for the 3d printed top lid are [located here](../../3d-print-files/drone-top-lid/).
- Replaced the stock 12mm payload carbon fiber tubes that came with the drone with longer 330mm ones from Amazon.
- Bought a longer 6-Pin JST-GH Twisted Pair - MRC0212 - 1000mm length cable from 3DR in order to make the serial connection from the gimbal to the Kore carrier board. Its a 6 pin connector and wire designed for I2C, but I removed 3 wires and swapped TX/RX on one end to make it work for the gimbal.
- Cut an 8"x8" sheet of ABS plastic down to a 2"x8" and a 3"x8" strip, and mounted them to the payload carbon fiber tubes with pipe clamps.
- Ran USB cables with USB-C and Micro USB ends to the front ABS plastic sheet. Both USB cables connect to the Raspberry Pi in the drone frame. Connect the USB-C cable to the USB 3.0 port (the blue one) on the Raspberry Pi.
- Mounted an Intel Realsense 435 Depth Camera to the front ABS plastic sheet.
- Mounted the HereFlow module and TFMini-S LiDAR to the ABS plastic sheets.
- Mounted the Gremsy Dampening plate and HDMI Hyper Quick release (see next video for more details though).
- Disabled the HereFlow Range Finder (but left the optical flow components active). Moved the TFMini-S from RNGFND2 to RNGFND1
- Setup the TFMini-S LiDAR to be a DroneCAN device using a [Matek AP_PERIPH CAN Node L431 Board](https://www.mateksys.com/?portfolio=can-l431)
  - You must first install the latest firmware to enable seeing the rangefinder parameters.
  - Download the latest firmware from here for the L431 board (download the .bin file): https://firmware.ardupilot.org/AP_Periph/stable/MatekL431-Rangefinder/
  - In Mission Planner, go to Setup->Optional Hardware->DroneCAN/UAVCAN
  - Connect to the CAN interface (CAN1 or CAN2) that your device L431 device is connected to.
  - In the menu button on the row for your device, press update. Select No when it asks to search the internet for an update.
  - You will be prompted for the firmware file to load. Select the .bin file downloaded earlier.
  - After updating, select the menu button again to open the parameters for the L431 node.
  - Set RNGFND1_TYPE to 20 and press write params.
  - Refresh params in the L431 and then also set:
    - RNGFND_BAUDRATE=115200
    - RNGFND_PORT=2
    - RNGFND_GNDCLEAR=set to distance in centimeters that your rangefinder reads to the ground.
    - RNGFND_MAX_CM=600
    - RNGFND_MIN_CM=10
  - Now go into Mission Planner->Config->Full Parameter List
    - Set RNGFND2_TYPE=24
  - If you are going to setup multiple rangefinders, then you must open the DroneCAN parameters for the device and set the CAN node ID to a unique number. Then you must set RNGFND1_ADDR to the node ID you assigned to the L431 device. For example I used 45 for my TFMini-S and 46 for my HereFlow rangefinder. Dont use an ID for an existing device listed in the Setup->Optional Hardware->DroneCAN/UAVCAN list either.
  - You dont want two identical lidar pointing in the same direction. The most likely outcome is that the lidar will become confused if they pickup the laser sent from the other lidar.




# Supporting Materials
- [ArduPilot Configuration](../ArduPilot-Config/ArduPilot-Config.md) - This page contains a consolidated list of the all of the configuration done in ArduPilot throughout the videos.


# References 
- Download the latest firmware [from here for the L431 board (download the .bin file)](https://firmware.ardupilot.org/AP_Periph/stable/MatekL431-Rangefinder/)
- [ArduPilot GPS Blending Document](https://ardupilot.org/copter/docs/common-gps-blending.html)