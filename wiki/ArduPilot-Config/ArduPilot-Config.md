This page contains a consolidated list of the all of the configuration done in ArduPilot throughout the videos. 
Use this to easily setup a new flight controllers.

# Custom Firmware
You will need to build your own custom firmware from [custom.ardupilot.org](http://custom.ardupilot.org/) in order to enable the DID_* parameters for Open Drone ID.
- Press "Add a build"
- For vehicle select Copter
- For branch Select the latest stable branch (i.e., Copter 4.5 stable)
- For board select CubeOrangePlus
- Under the Ident category, check the box for OpenDroneID (Remote ID)
- Press the "Generate Build" button
- Download the generated arducopter.apj file.
- In Mission Planner, go to Setup->Install Firmware
- Press "Load Custom Firmware"
- Select the apj file you downloaded and flash it to the board


# Initial Setup
After flashing firmware for the first time, use Mission Planner to configure several items:
- Go to Setup tab.
- Expand the Mandatory Hardware menu item.
  - On Frame Type menu item:
    - Select the Hexacopter X pattern.
  - On Initial Tune Parameters menu item:
    - Airscrew Inch Size: 24
    - Battery Cellcount: 12 (or 6 when testing with a 6s battery)
    - Battery cell fully discharged voltage: 3.3
    - Check the option to "Add suggested settings for 4.0 and up (Battery failsafe and Fence)".
    - Press the "Calculate Initial Parameters" button, and then the "Write to FC" button on the popup window.
  - On Accel Calibration menu item:
    - Press Calibrate Accel (use this for when you can manipulate the drone orientation)
    - Press Calibrate Level
    - Press Simple Accel Cal (use this in lieu of Calibrate Accel for large drone or simple bench testing)
    - Docs on accelerometer calibration [can be found here](https://ardupilot.org/copter/docs/common-accelerometer-calibration.html).    
  - On Compass menu item:
    - TODO - swap compasses later to use the external one higher priority than the one on cube once the GPS is installed
    - Press start on the Onboard Mag Calibration, calibrate, and reboot. Docs on compass calibration [can be found here](https://ardupilot.org/copter/docs/common-compass-calibration-in-mission-planner.html).
  - On Radio Calibration menu item:
    - Prior to calibrating, I had to reverse the joystick outputs in the Herelink controller for the Y (throttle rc2) and R (pitch rc3) axis. Otherwise the values were reversed.
    - Press the Calibrate Radio button. Move joysticks and input buttons to their limits. Then press the Click when Done button.
    - Docs on radio calibration [can be found here](https://ardupilot.org/copter/docs/common-radio-control-calibration.html).
    

# Parameter Settings
To set these parameters in mission planner, navigate to the Config tab, and then the Parameter List menu option.
Note: If you are using a fresh installation of mission planner you will have to enable this page by setting Config->Planner->Layout to “Advanced”

## Parameters - Kore carrier board voltage and current sensors
The default params recommended for battery monitoring are on the Kore carrier board page.
However, with the defaults I was getting negative current readings. Per this post I set the BATT_AMP_OFFSET to 0.37. There is also a recommendation to set BATT_AMP_PERVOLT to 67 but I did not do that.
https://discuss.cubepilot.org/t/negative-current-reading-on-kore-carrier-board/2299/11
You do not need to set these if you are going to use the settings below for the Tattu Smart Battery. That battery has a BMS from which ArduPilot can get it's status through DroneCAN.

|Parameter Name|Value|Description|
|---|---|---|
|BATT_MONITOR|4|Set this first, and then write the params so the other ones below show. Must reboot the board after changing. 4 = Analog voltage and current.|
|BATT_AMP_OFFSET|0.37|Kore docs recommend 0.45 but this caused negative current readings on my board.|
|BATT_AMP_PERVLT|50||
|BATT_CURR_PIN|15|Kore docs recommend 3, but I had to set to 15 to work with Cube Orange Plus.|
|BATT_VOLT_MULT|15.3||
|BATT_VOLT_PIN|14|Kore docs recommend 2, but I had to set to 14 to work with Cube Orange Plus.|

> If you are using the Tattu Smart Battery outlined below, you should skip setting these BATT_* parameters for the Kore Carrier Board

## Parameters - Fence
A fence is a virtual boundary set in the flight control system that restricts the area within which an unmanned aerial vehicle (UAV) can operate, helping to ensure it stays within a predefined safe zone and enhancing flight safety. If the UAV attempts to cross this boundary, the system can trigger predefined actions like returning to launch or landing. Upon Fence breach, selectable actions are taken.
|Parameter Name|Value|Description|
|---|---|---|
|FENCE_ENABLE|1|Enable or disable the fence functionality.|
|FENCE_ACTION|4|4 = Brake or Land. Set to 0 for report only.|
|FENCE_ALT_MAX|30|Maximum altitude before geofence triggers.|
|FENCE_MARGIN|3|Distance that the autopilot should maintain from the fence to avoid a breach.|
|FENCE_RADIUS|100|Radius of the geofence.|

## Parameters - Enable DroneCAN (Needed for Basically everything below)
|Parameter Name|Value|Description|
|---|---|---|
|CAN_P1_DRIVER|1||
|CAN_P2_DRIVER|2||
|CAN_D1_PROTOCOL|1|DroneCAN|
|CAN_D2_PROTOCOL|1|DroneCAN|



## Parameters - Here4 GPS
|Parameter Name|Value|Description|
|---|---|---|
|BRD_SAFETY_DEFLT|0|There is no safety switch on the Here4 GPS so we disable it. (BRD_SAFETYENABLE in older firmware versions)|
|GPS_TYPE|9||
|NTF_LED_TYPES|231||

<!--
|XXX|XXX|XXX|
-->

## Parameters - Onboard OLED Display
|Parameter Name|Value|Description|
|---|---|---|
|NTF_DISPLAY_TYPE|1|SSD1306 OLED Connected to I2C|


## Parameters - Motors
|Parameter Name|Value|Description|
|---|---|---|
|CAN_D1_UC_ESC_BM|63|Bitmask that determines which autopilot servo/motor output signals are sent to the DroneCAN ESCs. 63 = ESC 1 through 6.|
|CAN_D1_UC_OPTION|128|Set options for the DroneCAN driver for Hobbywing ESC.|


## Parameters - Cube ID
Be sure to build and load the custom firmware as described above. Otherwise, you will not see any of the DID_* parameters.
|Parameter Name|Value|Description|
|---|---|---|
|DID_ENABLE|1|Enable Open Drone ID|
|DID_CANDRIVER|1|DroneCAN driver index, 0 to disable DroneCAN.|
|DID_OPTIONS|6|6 sets AllowNonGPSPosition and LockUASIDOnFirstBasicIDRx. First setup the above two params, setup your Drone ID info in mission planner, verify it shows in Drone Scanner, and then set this bit. After your DID_UAS_ID is persisted, the LockUASIDOnFirstBasicIDRx will be unchecked in the params and this value set back to a 2.|

You can optionally set the DID_OPTIONS bitmask value as well for EnforceArming, AllowNonGPSPosition, and LockUASIDOnFirstBasicIDRx.
- EnforceArming = set to enforce arming checks
- AllowNonGPSPosition = allow drone to be armed without a GPS position. If you want to be able to arm without the operator location set this bit. Useful when testing flight controller indoors and not actually flying. You'll hear your Herelink repeat the error "ODID Lost Operator Location" which can get annoying after awhile.
- LockUASIDOnFirstBasicIDRx = To meet FAA requirements for manufacturers, a persistent ID needs to be recorded in Flight system. To achieve this with CubeID + Ardupilot setup. Ardupilot's persistent storage feature is used. After the setting, the first reception of Basic ID containing Drone ID and other details (from Mission Planner or any other GCS) will be persistently recorded. Please note that once set the persistent parameters can't be rolled back. Once the UAS ID is persisted, this will be unchecked and the values stored in the persistent.parm file on the flight controller. It will persist DID_UAS_ID, DID_UAS_ID_TYPE, and DID_UA_TYPE.


## Parameters - Here Flow
|Parameter Name|Value|Description|
|---|---|---|
|RNGFND1_TYPE|24|Type of connected rangefinder. Reboot flight controller after setting this for rest of the params to show.|
|RNGFND1_MIN_CM|5|Minimum distance in centimeters that rangefinder can reliably read.|
|RNGFND1_MAX_CM|200|Maximum distance in centimeters that rangefinder can reliably read.|
|RNGFND1_GNDCLEAR|10|Optional - This parameter sets  the expected range measurement(in cm) that the range finder should return when the vehicle is on the ground.|
|FLOW_TYPE|6|Enable optical flow camera.|


## Parameters - TFMini-S LiDAR
|Parameter Name|Value|Description|
|---|---|---|
|SERIAL4_PROTOCOL|9|What protocol Serial4 port should be used for. Change from -1 (GPS) to 9 (Lidar)|
|SERIAL4_BAUD|115|The baud rate used for Serial4. 115200 baud.|
|RNGFND2_TYPE|20|Type of connected rangefinder. 20=Benewake-Serial. Reboot flight controller after setting this for rest of the params to show.|
|RNGFND2_MIN_CM|10|Minimum distance in centimeters that rangefinder can reliably read. 10 for TFminiPlus|
|RNGFND2_MAX_CM|600|This is the distance in centimeters that the rangefinder can reliably read. 600 for outdoors.|
|RNGFND2_GNDCLEAR|10|Optional - This parameter sets  the expected range measurement(in cm) that the range finder should return when the vehicle is on the ground.|

## Parameters - Tattu 12s 16000mAh Smart Battery
These are the settings I used for the Tattu Plus 1.0 Compact Version 16000mAh 44.4V 15C 12S1P Lipo Smart Battery Pack With AS150U Plug.
|Parameter Name|Value|Description|
|---|---|---|
|BATT_MONITOR|8|DroneCAN|
|BATT_AMP_OFFSET|0|This may not show up once you set BATT_MONITOR to 8. Thats OK.|
|BATT_AMP_PERVLT|1|This may not show up once you set BATT_MONITOR to 8. Thats OK.|
|BATT_ARM_VOLT|44.3|Minimum battery voltage required to arm the aircraft.|
|BATT_CAPACITY|15800|The Tattu 12s battery has 16000 mah.|
|BATT_CRT_VOLT|42|Battery voltage that triggers a critical battery failsafe.|
|BATT_CURR_MULT|-1|Multiplier applied to all current related reports. Needed otherwise you get negative current readings from the Tattu battery.|
|BATT_FS_CRT_ACT|1|Action to perform if the critical battery failsafe is hit. 1 = Land|
|BATT_FS_LOW_ACT|2|Action to perform if the low battery failsafe is hit. 2 = RTL|
|BATT_LOW_VOLT|43.2|Battery voltage that triggers a low battery failsafe.|
|BATT_SERIAL_NUM|-1|Leave at -1 unless you have multiple DroneCAN batteries in the drone.|
|MOT_BAT_VOLT_MAX|50.4|Battery voltage compensation maximum voltage. Set to 4.2 * cell count.|
|MOT_BAT_VOLT_MIN|39.6|Battery voltage minimum compensation voltage. Set to 3.3 * cell count.|


# Factory Reset the Parameters
If, for some reason, you ever want to reset all of the parameters to their defaults you can follow any of the methods [listed here](https://ardupilot.org/copter/docs/common-parameter-reset.html).

To reset all params to defaults in MavProxy, first install MavProxy and then open MavProxy and run these commands:
- link add COM6
- param show FORMAT_VERSION
- param set FORMAT_VERSION 0
- reboot




