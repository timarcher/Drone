This page contains details on the setup of the Here 4 GPS and Here 4 Base.

The Here 4 GPS is a professional High Precision Dual-band RTK Navigation module. It supports multiple GNSS options such as BeiDou, Galileo, GLONASS, GPS, QZSS.

The Here 4 Base employs RTK (Real-Time Kinematic) technology to offer more precise position estimation compared to standard GNSS systems. Its potential for centimeter-level accuracy greatly enhances flight precision. The Here 4 supports L1 and L5 bands. Utilizing the L5 band delivers improved performance under challenging urban environments. The L5 signals fall within the protected ARNS (aeronautical radio navigation service) frequency band, leading to less RF interference.


# YouTube Video
- [Hexacopter Drone Build Project – Part 5 Here 4 GPS and Base](https://www.youtube.com/watch?v=yGW7yLQpPdI)

# Notes
- If you are going to install dual GPS units, you can take advantage of GPS for Yaw.
- When using dual Here4 units to take advantage of GPS for yaw, set the following:
  - Both units MUST be on the same physical CAN bus from the autopilot. I have mine connected to CAN1.
  - The antennas must be separated by at least 30cm on the vehicle.
  - Ensure no SERIAL ports are setup with GPS protocol (“5”). I had to set SERIAL3_PROTOCOL to -1.
  - Set the following:
    - GPS1_TYPE = 22 (“DroneCAN moving baseline base”)
    - GPS2_TYPE = 23 (“DroneCAN moving baseline rover”)
    - GPS_AUTO_CONFIG = 2 (AutoConfig DroneCAN)
    - GPS_AUTO_SWITCH = 1
    - EK3_SRC1_YAW = 3 (GPS with compass fallback)
    - Set the GPS1_POS_X/Y/Z and GPS2_POS_X/Y/Z parameters for the GPS antennas (see Sensor Position Offset are here). You must establish the relative positions of each GPS location on the vehicle with respect the vehicle’s motion.
    - You will also need to set the GPS1_CAN_OVRIDE and GPS2_CAN_OVRIDE so that the same gps units also map to GPS 1 and GPS2.

# Supporting Materials
- [ArduPilot Configuration](../ArduPilot-Config/ArduPilot-Config.md) - This page contains a consolidated list of the all of the configuration done in ArduPilot throughout the videos.

# References 
- User guide for the Here 4 GPS [can be found here](https://docs.cubepilot.org/user-guides/here-4/here-4-manual).
- User guide for the Here 4 Base [can be found here](https://docs.cubepilot.org/user-guides/here-4/here-4-base).
- [ArduPilot GPS Blending Document](https://ardupilot.org/copter/docs/common-gps-blending.html).
- [GNSS View Tool - use to see constellations in your area](https://app.qzss.go.jp/GNSSView/gnssview.html).
- [GPS for Yaw](https://ardupilot.org/copter/docs/common-gps-for-yaw.html).
- [Supported GPS in ArduPilot](https://ardupilot.org/copter/docs/common-positioning-landing-page.html#common-positioning-landing-page)
