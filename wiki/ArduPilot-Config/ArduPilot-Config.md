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
    - Swap compasses later to use the external one higher priority than the one on cube once the GPS is installed.
    - Press start on the Onboard Mag Calibration, calibrate, and reboot. Docs on compass calibration [can be found here](https://ardupilot.org/copter/docs/common-compass-calibration-in-mission-planner.html).
  - On Radio Calibration menu item:
    - Prior to calibrating, I had to reverse the joystick outputs in the Herelink controller for the Y (throttle rc2). Otherwise the values were reversed.
    - Press the Calibrate Radio button. Move joysticks and input buttons to their limits. Then press the Click when Done button.
    - Docs on radio calibration [can be found here](https://ardupilot.org/copter/docs/common-radio-control-calibration.html).
    - Be sure to test the controls in Mission Planner. Move the transmitter’s roll, pitch, throttle and yaw sticks and ensure the green bars move in the correct direction:
      - For roll, throttle and yaw channels, the green bars should move in the same direction as the transmitter’s physical sticks.
      - For pitch, the green bar should move in the opposite direction to the transmitter’s physical stick.
      - If one of the green bars moves in the incorrect direction reverse the channel in the transmitter itself. If it is not possible to reverse the channel in the transmitter you may reverse the channel in ArduPilot by checking the “Reversed” checkbox (Plane and Rover only). If the checkbox is not visible it is possible to reverse the channel by directly changing the RCx_REVERSED parameter (where “x” is the input channel from 1 to 4).
    

# Parameter Settings
To set these parameters in mission planner, navigate to the Config tab, and then the Parameter List menu option.
Note: If you are using a fresh installation of mission planner you will have to enable this page by setting Config->Planner->Layout to “Advanced”

## Parameters - Herelink Telemetry
I changed the default baud rate from 57600 to 115200.
You must also change the baud rate on the air unit. To do this, open the herelink settings, go to Airunit, select 115200 for the baudrate and click Reset Baud.

|Parameter Name|Value|Description|
|---|---|---|
|SERIAL1_BAUD|115|The MAVLink over Herelink telemetry, changed from default of 57600 to 115200.|


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
|BATT_ARM_VOLT|44.3|Minimum battery voltage required to arm the aircraft.|
|BATT_CAPACITY|15800|The Tattu 12s battery has 16000 mah.|
|BATT_CRT_VOLT|42|Battery voltage that triggers a critical battery failsafe.|
|BATT_CURR_PIN|15|Kore docs recommend 3, but I had to set to 15 to work with Cube Orange Plus.|
|BATT_FS_CRT_ACT|1|Action to perform if the critical battery failsafe is hit. 1 = Land|
|BATT_FS_LOW_ACT|2|Action to perform if the low battery failsafe is hit. 2 = RTL|
|BATT_LOW_VOLT|43.2|Battery voltage that triggers a low battery failsafe.|
|BATT_SERIAL_NUM|-1|Leave at -1.|
|BATT_VOLT_MULT|15.2||
|BATT_VOLT_PIN|14|Kore docs recommend 2, but I had to set to 14 to work with Cube Orange Plus.|

> If you are using the Tattu Smart Battery outlined below, you should skip setting these BATT_* parameters for the Kore Carrier Board. If you wish, you may set the Tattu smart battery settings as described below under BATT_, and then set these values under BATT2_ instead of BATT_ to have a secondary battery monitor using the circuity on the Kore carrier board. If you do that, I recommend you set BATT2_MONITOR to a value of 3, monitoring the analog voltage only. The remaining capacity is more accurately measured through the smart battery, and so also trying to measure current through the Kore carrier board will show a remaining capacity on the 2nd battery monitor that is wrong because it resets between flight controller reboots.


## Parameters - Enable DroneCAN (Needed for Basically everything below)
|Parameter Name|Value|Description|
|---|---|---|
|CAN_P1_DRIVER|1|1st Driver.|
|CAN_P2_DRIVER|2|2nd Driver.|
|CAN_D1_PROTOCOL|1|DroneCAN.|
|CAN_D2_PROTOCOL|1|DroneCAN.|



## Parameters - Here4 GPS
|Parameter Name|Value|Description|
|---|---|---|
|BRD_SAFETY_DEFLT|0|There is no safety switch on the Here4 GPS so we disable it. (BRD_SAFETYENABLE in older firmware versions)|
|GPS1_TYPE|9|GPS type of 1st GPS.|
|NTF_LED_TYPES|231|Controls what types of LEDs will be enabled.|
|GPS_AUTO_CONFIG|2|Needed to enable RTK autocorrect, set to enable for DroneCAN as well.|

If using multiple GPS', as in my drone, also need to set additional params. In my drone, GPS1 (Node 119) is the GPS at the rear of the vehicle, and GPS2 (Node 118) is the GPS at the front of the vehicle.
|Parameter Name|Value|Description|
|---|---|---|
|GPS1_CAN_OVRIDE|119|Node ID for the 1st GPS. Set appropriately for your vehicle as the Node IDs might be different.|
|GPS2_TYPE|9|GPS type of 2nd GPS.|
|GPS2_CAN_OVRIDE|118|Node ID for the 1st GPS. Set appropriately for your vehicle as the Node IDs might be different.|
|GPS_AUTO_SWITCH|1|Set to Use Best.|

Additionally, you may wish to set the offsets of the sensors relative to the center of your Cube Orange.  Customize the value by measuring the offset from the center of your Cube Orange to the middle of the sensor.
|Parameter Name|Value|Description|
|---|---|---|
|GPS1_POS_X|-0.135|X position of the second GPS antenna in body frame. Positive X is forward of the origin. Units in meters.|
|GPS1_POS_Y|0.030|Y position of the second GPS antenna in body frame. Positive Y is to the right of the origin. Units in meters.|
|GPS1_POS_Z|-0.110|Z position of the second GPS antenna in body frame. Positive Z is down from the origin. Units in meters.|
|GPS2_POS_X|0.138|X position of the first GPS antenna in body frame. Positive X is forward of the origin. Units in meters.|
|GPS2_POS_Y|-0.036|Y position of the first GPS antenna in body frame. Positive Y is to the right of the origin. Units in meters.|
|GPS2_POS_Z|-0.110|Z position of the first GPS antenna in body frame. Positive Z is down from the origin. Units in meters.|


New RTK can be used to estimate yaw, in addition to providing position information. This removes the need for a compass which may suffer from magnetic interference from the ground or the vehicle’s motors and ESCs. Set the following to use this as well:
|Parameter Name|Value|Description|
|---|---|---|
|GPS1_TYPE|22|DroneCAN moving baseline base|
|GPS2_TYPE|23|DroneCAN moving baseline rover|
|GPS_AUTO_CONFIG|2|Autoconfig DroneCAN|
|GPS_AUTO_SWITCH|1|Use Best|

> Be sure you set the GPS1_POS_X/Y/Z and GPS2_POS_X/Y/Z parameters for the GPS antennas (see Sensor Position Offset are here) as described above. You must establish the relative positions of each GPS location on the vehicle with respect the vehicle’s motion.


I have my 2nd Here4 GPS mounted backwards at the front of the drone (to position it slightly further away from the onboard electronics). I need to set the appropriate orientation then:
|Parameter Name|Value|Description|
|---|---|---|
|COMPASS_ORIENT2|4|Compass is rotated 180 degrees and pointing backwards, so we set this to Yaw180.|



<!--
|XXX|XXX|XXX|
-->

## Parameters - Onboard OLED Display
|Parameter Name|Value|Description|
|---|---|---|
|NTF_DISPLAY_TYPE|1|SSD1306 OLED Connected to I2C.|


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
|RNGFND1_MIN_CM|10|Minimum distance in centimeters that rangefinder can reliably read.|
|RNGFND1_MAX_CM|200|Maximum distance in centimeters that rangefinder can reliably read.|
|RNGFND1_GNDCLEAR|29|Optional - This parameter sets  the expected range measurement(in cm) that the range finder should return when the vehicle is on the ground.|
|FLOW_TYPE|6|Enable optical flow camera.|

Additionally, you may wish to set the offsets of the sensors relative to the center of your Cube Orange.  Customize the value by measuring the offset from the center of your Cube Orange to the middle of the sensor.
|Parameter Name|Value|Description|
|---|---|---|
|FLOW_POS_X|-0.140|X position of the optical flow sensor focal point in body frame. Positive X is forward of the origin. Units in meters.|
|FLOW_POS_Y|-0.075|Y position of the optical flow sensor focal point in body frame. Positive Y is to the right of the origin. Units in meters.|
|FLOW_POS_Z|0.206|Z position of the optical flow sensor focal point in body frame. Positive Z is down from the origin. Units in meters.|


## Parameters - TFMini-S LiDAR
|Parameter Name|Value|Description|
|---|---|---|
|SERIAL4_PROTOCOL|9|What protocol Serial4 port should be used for. Change from -1 (GPS) to 9 (Lidar)|
|SERIAL4_BAUD|115|The baud rate used for Serial4. 115200 baud.|
|RNGFND2_TYPE|20|Type of connected rangefinder. 20=Benewake-Serial. Reboot flight controller after setting this for rest of the params to show.|
|RNGFND2_MIN_CM|10|Minimum distance in centimeters that rangefinder can reliably read. 10 for TFminiPlus|
|RNGFND2_MAX_CM|600|This is the distance in centimeters that the rangefinder can reliably read. 600 for outdoors.|
|RNGFND2_GNDCLEAR|29|Optional - This parameter sets  the expected range measurement(in cm) that the range finder should return when the vehicle is on the ground.|

If using the Matek AP_PERIPH CAN Node L431 Board to convert your TFMini-S to a DroneCAN device, then set these instead:
|Parameter Name|Value|Description|
|---|---|---|
|RNGFND2_TYPE|24|Type of connected rangefinder. 24=DroneCAN. Reboot flight controller after setting this for rest of the params to show.|
|RNGFND2_MIN_CM|10|Minimum distance in centimeters that rangefinder can reliably read. 10 for TFminiPlus|
|RNGFND2_MAX_CM|600|This is the distance in centimeters that the rangefinder can reliably read. 600 for outdoors.|
|RNGFND2_GNDCLEAR|45|Optional - This parameter sets  the expected range measurement(in cm) that the range finder should return when the vehicle is on the ground.|

Additionally, you may wish to set the offsets of the sensors relative to the center of your Cube Orange.  Customize the value by measuring the offset from the center of your Cube Orange to the middle of the sensor.
|Parameter Name|Value|Description|
|---|---|---|
|RNGFND1_POS_X|-0.160|X position of the rangefinder in body frame. Positive X is forward of the origin. Units in meters.|
|RNGFND1_POS_Y|0|Y position of the rangefinder in body frame. Positive Y is to the right of the origin. Units in meters.|
|RNGFND1_POS_Z|0.211|Z position of the rangefinder in body frame. Positive Z is down from the origin. Units in meters.|



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


## Parameters - Flytron STROBON Cree V2 Lights
|Parameter Name|Value|Description|
|---|---|---|
|SERVO9_FUNCTION|56|Configure for RC Pass thru. 56 = RCIN6 which means RC channel 6 gets output to SERVO9.|

> On the Kore carrier board SERVO9 - SERVO15 are mapped to the 6 auxiliary outputs.
> For testing, on the Herelink controller, go to the settings and map a button to a channel. In my testing I mapped a short press of the D button to RC channel 6, and it toggles between a value of 1000 and 2000 when pressed. And then in Ardupilot, I set SERVO9_FUNCTION to 56, which means to pass RC channel 6 (RCIN6) through to SERVO9. SERVO9 corresponds to the first auxiliary output on the Kore carrier board.


## Parameters - Flight Modes
I have my flight modes configured as follows. This requires some config in ArduPilot as well as the HereLink controller. You can also set these up in Mission Planner on the Setup->Flight Modes screen.

|Parameter Name|Value|Description|
|---|---|---|
|FLTMODE_CH|5|RC Channel to use for flight mode control. Default is 5.|
|FLTMODE1|5|Flight mode when pwm of Flightmode channel(FLTMODE_CH) is <= 1230. Set to Loiter.|
|FLTMODE2|15|Flight mode when pwm of Flightmode channel(FLTMODE_CH) is >1230, <= 1360. Set to AutoTune.|
|FLTMODE3|2|Flight mode when pwm of Flightmode channel(FLTMODE_CH) is >1360, <= 1490. Set to AltHold.|
|FLTMODE4|3|Flight mode when pwm of Flightmode channel(FLTMODE_CH) is >1490, <= 1620. Set to Auto.|
|FLTMODE5|6|Flight mode when pwm of Flightmode channel(FLTMODE_CH) is >1620, <= 1749. Set to RTL.|
|FLTMODE6|9|Flight mode when pwm of Flightmode channel(FLTMODE_CH) is >=1750. Set to Land.|

On the HereLink controller I configured the A, B, and Home buttons to control my flight modes using the following steps:
- On the HereLink controller in the settings area, go to the buttons tab.
-  Flight Mode 1 - Loiter - PWM 0-1230 - Mapped to button A short press, active value 1100, mark as default button
-  Flight Mode 2 - AutoTune - PWM 1231-1360 - Mapped to button A long press, active value 1300
-  Flight Mode 3 - AltHold - PWM 1361-1490 - Mapped to button B short press, active value 1425
-  Flight Mode 4 - Stabilize - PWM 1491-1620 - Mapped to button B long press, active value 1550
-  Flight Mode 5 - Smart_RTL - PWM 1621-1749 - Mapped to button home short press, active value 1675
-  Flight Mode 6 - Land - PWM 1750+ - Mapped to button home long press, active value 1800


## Parameters - RC Failsafe
- In Mission Planner go to the Setup->FailSafe tab. Configure the radio failsafe to Enabled always RTL, and an FS Pwm of 975

|Parameter Name|Value|Description|
|---|---|---|
|RC_FS_TIMEOUT|1|RC failsafe will trigger this many seconds after loss of RC.|
|FS_THR_ENABLE|1|The throttle failsafe allows you to configure a software failsafe activated by a setting on the throttle input channel. Set to Enabled, always RTL.|
|FS_THR_VALUE|975|The PWM level in microseconds on channel 3 below which throttle failsafe triggers.|


## Parameters - GeoFence
A fence is a virtual boundary set in the flight control system that restricts the area within which an unmanned aerial vehicle (UAV) can operate, helping to ensure it stays within a predefined safe zone and enhancing flight safety. If the UAV attempts to cross this boundary, the system can trigger predefined actions like returning to launch or landing. Upon Fence breach, selectable actions are taken.

- In Mission Planner go to the Config->GeoFence tab. Configure the GeoFence settings to control the distance your drone is allowed to go from it's launch point.

|Parameter Name|Value|Description|
|---|---|---|
|FENCE_ACTION|4|4 = Brake or Land. Set to 0 for report only.|
|FENCE_ALT_MAX|120|Maximum altitude allowed before geofence triggers. Value is in meters. I set to 30 when initially testing drone.|
|FENCE_ALT_MIN|-10|Minimum altitude allowed before geofence triggers. Value is in meters.|
|FENCE_AUTOENABLE|0|Auto-enable of fences. Set to Disabled.|
|FENCE_ENABLE|1|Allows you to enable (1) or disable (0) the fence functionality.|
|FENCE_MARGIN|3|Distance that autopilot's should maintain from the fence to avoid a breach. Value is in meters.|
|FENCE_RADIUS|100|Circle fence radius which when breached will cause an RTL. Value is in meters.|
|FENCE_TYPE|7|Bitmask. Set to Max Altitude, Circle Centered on Home, and Inclusion/Exclusion Circles+Polygons|


## Parameters - Additonal RC Channel Options
- In Mission Planner you can also go to the Config->User Params tab and map actions to other channels as desired. For example you could map channel 7 to fence enable/disable. This would be the same as setting RC7_OPTION to a value of 11. Other fun things, for example, you could map it to the lost copter sound.

|Parameter Name|Value|Description|
|---|---|---|
|RC7_OPTION|11|Function assigned to this RC channel. Set to Fence Enable.|


## Parameters - Waypoint Navigation
I have adjusted these parameters to be about half the default value to make my drone move more slowly during missions.

|Parameter Name|Value|Description|
|---|---|---|
|WPNAV_SPEED|500|Defines the speed in cm/s which the aircraft will attempt to maintain horizontally during a WP mission.|
|WPNAV_SPEED_UP|150|Defines the speed in cm/s which the aircraft will attempt to maintain while climbing during a WP mission.|
|WPNAV_SPEED_DN|100|Defines the speed in cm/s which the aircraft will attempt to maintain while descending during a WP mission.|
|WPNAV_ACCEL|125|Defines the horizontal acceleration in cm/s/s used during missions.|
|WPNAV_ACCEL_Z|75|Defines the vertical acceleration in cm/s/s used during missions.|


## Parameters - Gremsy T7 Gimbal
|Parameter Name|Value|Description|
|---|---|---|
|CAM1_TYPE|5|Camera shutter (trigger) type of MAVLink.|
|MNT1_DEFLT_MODE|2|Mount default operating mode on startup and after control is returned from autopilot. 2 is MavLink targeting. 3 is RC Targeting.|
|MNT1_OPTIONS|2|Return to neutral position on RC failsafe.|
|MNT1_PITCH_MAX|20|Mount Pitch angle maximum.|
|MNT1_PITCH_MIN|-90|Mount Pitch angle minimum.|
|MNT1_RC_RATE|90|Pilot rate control's maximum rate. Deg/s.|
|MNT1_TYPE|6|For Gremsy. Reboot after changing this param.|
|MNT1_YAW_MAX|90|Mount Yaw angle maximum.|
|MNT1_YAW_MIN|-90|Mount Yaw angle minimum.|
|SERIAL2_BAUD|921|Communication at 921600 bps.|
|SERIAL2_PROTOCOL|2|Mavlink2|
|SERIAL2_OPTIONS|0|Default|

http://192.168.200.101/

## Parameters - Board Boot Delay
|Parameter Name|Value|Description|
|---|---|---|
|BRD_BOOT_DELAY|5000|This adds a delay in milliseconds to boot to ensure peripherals initialise fully. Value in milliseconds.|



# Factory Reset the Parameters
If, for some reason, you ever want to reset all of the parameters to their defaults you can follow any of the methods [listed here](https://ardupilot.org/copter/docs/common-parameter-reset.html).

To reset all params to defaults in MavProxy, first install MavProxy and then open MavProxy and run these commands:
- link add COM6
- param show FORMAT_VERSION
- param set FORMAT_VERSION 0
- reboot




