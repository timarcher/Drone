This page contains details on the initial setup of the Cube Orange Plus and Kore Carrier Board.


# YouTube Video
- [Hexacopter Drone Build Project – Part 4 Cube Orange Plus and Kore Carrier Board Initial Setup](https://www.youtube.com/watch?v=5t4QqKYQOWc)

# Notes
- Its important to note that the auxiliary ports of the Kore carrier board map to servo ports starting at 9. So:
  - Kore Carrier Board Auxiliary Port 1 = SERVO9
  - Kore Carrier Board Auxiliary Port 2 = SERVO10
  - Kore Carrier Board Auxiliary Port 3 = SERVO11
  - Kore Carrier Board Auxiliary Port 4 = SERVO12
  - Kore Carrier Board Auxiliary Port 5 = SERVO13
  - Kore Carrier Board Auxiliary Port 6 = SERVO14
- You must supply 5v power to the auxiliary ports if you wish to power devices connected to those ports. I applied a simple 5v supply to auxiliary port 6. Applying power to one auxiliary port will power them all. It is recommended to use a BEC to supply power to these ports if you will be attaching noisy devices such as servos.

# Supporting Materials
- [ArduPilot Configuration](../ArduPilot-Config/ArduPilot-Config.md) - This page contains a consolidated list of the all of the configuration done in ArduPilot throughout the videos.

# References 
## Herelink User Guides
- User guides for the Herelink [can be found here](https://docs.cubepilot.org/user-guides/herelink/herelink-user-guides).
- User guides for the Kore Carrier Board [can be found here](https://docs.cubepilot.org/user-guides/carrier-boards/kore-carrier-board).
- Details about the Kore carrier board [can be found here](https://docs.spektreworks.com/carrier_board_v1_3_1/).
- You can download STL files to 3d print a case for the Kore carrier board [from here](https://www.spektreworks.com/products/multi-rotor-pixhawk21-carrier-board). We dont use this in this project, but it may be an option for yours.

## ArduPilot References
- [ArduPilot Tuning Process Instructions](https://ardupilot.org/copter/docs/tuning-process-instructions.html)