This page contains details on the setup of the Cube ID Remote ID solution. This device broadcasts information about UAVs in flight through a Bluetooth 5.2 dual-mode unit, and supports both CAN and serial protocols. This page installs the device which uses the CAN protocol.

# YouTube Video
- [Hexacopter Drone Build Project – Part 8 Cube ID](https://youtu.be/XXjpxRVWvc4)

# Notes
- You must build and install a custom ArduPilot firmware in order for the DID_* config parameters to be available to set. See the [ArduPilot Configuration](../ArduPilot-Config/ArduPilot-Config.md) for how to do this.
- Use the Drone Scanner app on your mobile phone to verify if your drone is broadcasting Remote ID information.
- See the [ArduPilot Configuration](../ArduPilot-Config/ArduPilot-Config.md) page for details on parameters to set to enable Open Drone ID (Remote ID). You may also wish to set the DID_OPTIONS parameter to be different from the defaults based on your needs.
  - Before setting the DID_OPTIONS parameter, setup your Drone ID info in mission planner, verify it shows in Drone Scanner, and then set this bit.
- In Mission Planner, on the Data tab, click on the Drone ID tab. Set the parameters here that are to be broadcast:
  - UAS ID Tab
    - UAS ID - Set to your FAA Registration number. This wll show under the Serial Number field in Drone Scanner.
    - UAS ID Type - CAA_REGISTRATION_ID
    - UA Type - HELICOPTER_OR_MULTIROTOR. This wll show under the Type field in Drone Scanner.
  - Operations Tab
    - Operator ID - Put your FAA registration number here. This wll show under the Operator ID field in Drone Scanner.
    - Oper. ID Type - CAA
    - Self ID Desc - [Put your name in this field]. This wll show under the Operation Description field in Drone Scanner.
    - Self ID Type - TEXT
- Once you persist the settingsUAS ID with LockUASIDOnFirstBasicIDRx, this will be unchecked and the values stored in the persistent.parm file on the flight controller. It will persist DID_UAS_ID, DID_UAS_ID_TYPE, and DID_UA_TYPE. You will be unable to change/reset these later.


# Supporting Materials
- [ArduPilot Configuration](../ArduPilot-Config/ArduPilot-Config.md) - This page contains a consolidated list of the all of the configuration done in ArduPilot throughout the videos.


# References 
- Cube ID Documentation [can be found here](https://docs.cubepilot.org/user-guides/cube-id/cube-id).
- ArduPilot Remote ID setup information [can be found here](https://ardupilot.org/copter/docs/common-remoteid.html).
- ArduPilot custom firmware build site [can be found here](https://custom.ardupilot.org).


# About Remote ID
The FAA’s Remote ID requirements state that the following information must be included in the Remote ID broadcast when using a Remote ID module:
- Serial number of the Remote ID module
- Current location of the model (latitude, longitude, and altitude)
- Current velocity of the model
- Takeoff location of the model (which is presumably where the pilot is located)
- Time

Remote ID modules broadcast data using a Bluetooth or Wi-Fi signal that is intended to be received on a smartphone. Anyone with a smartphone who is running a Remote ID-capable app and is within range of the signal can potentially read the data from your model’s Remote ID module.

If your Remote ID module is broadcasting only the minimum required data listed previously, civilians reading Remote ID data will not be privy to your name or any private information; however, law enforcement officers will be able to cross-reference the Remote ID module serial number with the data in your FAA UAS registration.