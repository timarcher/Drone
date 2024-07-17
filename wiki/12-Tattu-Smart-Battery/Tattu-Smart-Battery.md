This page contains details on the setup of the Tattu smart battery. Tattu Plus batteries with AS150U connectors support DroneCAN which allows the autopilot to retrieve the battery’s total voltage, individual cell voltages, current, temperature and percentage of remaining capacity.

# YouTube Video
- [Hexacopter Drone Build Project – Part 12 Tattu Smart Battery](https://youtu.be/XXX)

# Notes
- I could NOT get the telemetry to reliably read on the CAN bus if the battery was connected to the same CAN port as the HobbyWing motors. In my configuration the motors, GPS, HereFlow, and Cube ID are all connected to CAN1, and the battery is connected to CAN2.
- Be sure to have both CAN ports enabled, and a different driver setup for each through these ArduPilot parameters:
    |Parameter Name|Value|Description|
    |---|---|---|
    |CAN_P1_DRIVER|1||
    |CAN_P2_DRIVER|2||
    |CAN_D1_PROTOCOL|1|DroneCAN|
    |CAN_D2_PROTOCOL|1|DroneCAN|
- On the wiring of the data pins from the battery:
  - CAN_H is the white wire
  - CAN_L is the yellow wire
  - The red wire is NOT connected. 

# Supporting Materials
- [ArduPilot Configuration](../ArduPilot-Config/ArduPilot-Config.md) - This page contains a consolidated list of the all of the configuration done in ArduPilot throughout the videos.

# References 
- Ardupilot Tattu DroneCAN battery guide [can be found here](https://ardupilot.org/plane/docs/common-tattu-dronecan-battery.html).

# Images
![alt text](./images/tattu-can-wiring.png)