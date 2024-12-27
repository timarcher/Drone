This page contains details on setting up the LightWare S45/B LiDAR.

# YouTube Video
- [Hexacopter Drone Build Project – Part 17 Obstacle Avoidance LiDAR](https://youtu.be/x13RS9YKt_g)

# Notes
- I connected the LiDAR to an Matek L431 AP_PERIPH board. This allows me to convert the serial interface of the LiDAR to DroneCAN.

- Setup the LightWare SF45/B LiDAR to be a DroneCAN device using a [Matek AP_PERIPH CAN Node L431 Board](https://www.mateksys.com/?portfolio=can-l431)
  - You must first install the latest firmware to enable seeing the proximity sensor parameters.
  - Download the latest firmware from here for the L431 board (download the .bin file): https://firmware.ardupilot.org/AP_Periph/stable/MatekL431-Proximity/
  - In Mission Planner, go to Setup->Optional Hardware->DroneCAN/UAVCAN
  - Connect to the CAN interface (CAN1 or CAN2) that your device L431 device is connected to.
  - In the menu button on the row for your device, press update. Select No when it asks to search the internet for an update.
  - You will be prompted for the firmware file to load. Select the .bin file downloaded earlier.
  - After updating, select the menu button again to open the parameters for the L431 node.
  - Refresh params in the L431 and then also set:
    - PRX_BAUDRATE=115200
    - PRX_PORT=2
    - PRX1_TYPE=8
    - PRX1_ORIENT=0
    - PRX1_YAW_CORR=0
    - PRX1_IGN_ANG1 and PRX1_IGN_WID1 parameters allow defining zones around the vehicle that should be ignored. For example to avoid a 20deg area to the right, set PRX1_IGN_ANG1 to 90 and PRX1_IGN_WID1 to 20.
  - Now go into Mission Planner->Config->Full Parameter List
    - Set PRX1_TYPE=14
- You can set various obstacle avoidance settings on the flight controller as well. I left all the defaults in place, which were:
  - AVOID_ALT_MIN=0 (Minimum altitude above which proximity based avoidance will start working. This requires a valid downward facing rangefinder reading to work. Set zero to disable)
  - AVOID_BEHAVE=1 (Avoidance behaviour of stop)
  - AVOID_DIST_MAX=5 (Distance from object at which obstacle avoidance will begin in non-GPS modes)
  - AVOID_ENABLE=3 (Bitmask for Fence and Proximity)
  - AVOID_MARGIN=2 (Vehicle will attempt to stay at least this distance (in meters) from objects while in GPS modes)
- To see what the proximity sensor sees, in Mission Planner press CTRL-F. Press the button in the popup window labeled "Proximity".
- ArduPilot recommends setting up an RC Channel to be able to turn on and off proximity avoidance.
  - Set RC8_OPTION=40
  - I then mapped Channel 8 to button C on the HereLink controller. 

# Supporting Materials
- [ArduPilot Configuration](../ArduPilot-Config/ArduPilot-Config.md) - This page contains a consolidated list of the all of the configuration done in ArduPilot throughout the videos.
- [3d Printed Lid](../../3d-print-files/drone-top-lid/Drone%20Top%20Lid.stl) - This is the lid to 3d print with mounting holes for the LiDAR.

# References 
- [Ardupilot LightWare SF45/B 350 Lidar Setup Page](https://ardupilot.org/copter/docs/common-lightware-sf45b.html)
- [LightWare Studio](https://lightwarelidar.com/resources-software/) - use this for testing your LiDAR through your PC and a USB connection.
- Download the latest proximity sensor firmware [from here for the L431 board (download the .bin file)](https://firmware.ardupilot.org/AP_Periph/stable/MatekL431-Proximity/)