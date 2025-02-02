This page contains a checklist to work through prior to flying the drone.


# Before Flight Prep Checklist – Do Before Heading to Field
1.	Portable Battery Charged
1.	Laptop Charged
1.	HereLink Charged
1.	Drone Battery Charged
1.	Review ArduPilot Configuration Below. Everything set appropriately for flight modes and failsafes?
1.	Will the Gimbal be needed? If not set MNT1_TYPE to 0.
1.	Field Equipment Packed? See list below.
1.	Field Tools Packed? See list below.
1.	Clean rangefinder, proximity sensor, and camera lens.


# Ground Control Station (GCS) Prep Checklist
1.	Enable Phone Mobile HotSpot
1.	Power on Travel Router/Wifi 
1.	Power On Laptop
1.	Is Laptop Connected to Wifi, Can access Internet?
1.	Setup RTK Base Tripod
1.	Connect Here4 Base to Laptop
1.	Connect Coax Cable from Here4 Base to GPS Antenna
1.	Start Mission Planner and Get a Ground Unit Fix


# Drone Flight Checklist
1.	Arms Extended
1.	Arms Secure and Locked in Place?
1.	Battery Installed and Secure
1.	Foam Prop Mounts Removed
1.	Props Positioned Out
1.	Gimbal Connected
1.	HDMI Cable Connected to Gimbal
1.	Power On Drone
1.	Power on HereLink Controller
1.	Connect Mission Planner GCS to HereLink Controller
1.	Is Video Feed Viewable in HereLink?
1.	Can Video Feed Swap to HDMI2 and Back to HDMI1 and Works Properly?
1.	Does Camera Trigger Button Work?
1.	Does Camera Menu Button Work?
1.	Does Camera Zoom Work?
1.	Does Gimbal Move Correctly?
1.	Does Camera Have an SD Card?
1.	Do Flight Modes Toggle Appropriately (Review Below Which Button Maps to Which Flight Modes)
1.	Did GPS Get a Fix?
1.	Is Automated Mission Uploaded Correctly?
1.	Do we want Fence On or Off?

 
# ArduPilot Configuration to Review
## Important ArduPilot FailSafe Params
- BATT_LOW_VOLT=43.2
- BATT_CRT_VOLT=42
- BATT_FS_LOW_ACT=2 - Action to perform if the low battery failsafe is hit. 2 = RTL
- BATT2_FS_LOW_ACT=2 - Action to perform if the low battery failsafe is hit. 2 = RTL
- BATT_FS_CRT_ACT=1 - Action to perform if the critical battery failsafe is hit. 1 = Land
- BATT2_FS_CRT_ACT=1 - Action to perform if the critical battery failsafe is hit. 1 = Land
- FS_THR_ENABLE=1 The throttle failsafe allows you to configure a software failsafe activated by a setting on the throttle input channel. Set to Enabled, always RTL. If the GPS position is not usable, the copter will change to Land Mode instead.
- FS_THR_VALUE=975 The PWM level in microseconds on channel 3 below which throttle failsafe triggers.
- RC_FS_TIMEOUT=1 RC failsafe will trigger this many seconds after loss of RC.


## Important ArduPilot RTL Params
- RTL_ALT=1500 The minimum alt above home the vehicle will climb to before returning. If the vehicle is flying higher than this value it will return at its current altitude. Value is in Centimeters.
- RTL_LOIT_TIME=5000 Time (in milliseconds) to loiter above home before beginning final descent. Value is in milliseconds.


# HereLink Button Setup
## HereLink Button Setup - Flight Modes
On the HereLink controller I configured the A, B, and Home buttons to control my flight modes using the following steps:
-  Flight Mode 1 - Loiter - PWM 0-1230 - Mapped to button A short press, active value 1100, mark as default button
-  Flight Mode 2 - AutoTune - PWM 1231-1360 - Mapped to button A long press, active value 1300
-  Flight Mode 3 - AltHold - PWM 1361-1490 - Mapped to button B short press, active value 1425
-  Flight Mode 4 - Stabilize - PWM 1491-1620 - Mapped to button B long press, active value 1550
-  Flight Mode 5 - Smart_RTL - PWM 1621-1749 - Mapped to button home short press, active value 1675
-  Flight Mode 6 - Land - PWM 1750+ - Mapped to button home long press, active value 1800


## HereLink Button Setup - Other Buttons
- A Short Press - Loiter Flight Mode
- B Short Press - AltHold Flight Mode
- Home Short Press - RTL  Flight Mode
- Home Long Press - Land Flight Mode
- C Short Press – Channel 8 – Enable/Disable Proximity Avoidance
- D Short Press – Channel 6 – Enable/Disable Navigation Lights
- D Long Press – Channel 7 – Enable/Disable Fence Mode


# Fence Setup
In Mission Planner go to the Config->GeoFence tab. Configure the GeoFence settings to control the distance your drone is allowed to go from it's launch point.
- FENCE_ACTION 4 4 = Brake or Land. Set to 0 for report only. 
- FENCE_ALT_MAX 120 Maximum altitude allowed before geofence triggers. Value is in meters. I set to 30 when initially testing drone. 
- FENCE_ALT_MIN -10 Minimum altitude allowed before geofence triggers. Value is in meters. 
- FENCE_AUTOENABLE 0 Auto-enable of fences. Set to Disabled. 
- FENCE_ENABLE 1 Allows you to enable (1) or disable (0) the fence functionality. 
- FENCE_MARGIN 3 Distance that autopilot's should maintain from the fence to avoid a breach. Value is in meters. 
- FENCE_RADIUS 100 Circle fence radius which when breached will cause an RTL. Value is in meters. 
- FENCE_TYPE 7 Bitmask. Set to Max Altitude, Circle Centered on Home, and Inclusion/Exclusion Circles+Polygons 


# Field Equipment to Pack
- Drone
- Battery
- Herelink Controller
- Here4 Base
- RTK GPS Antenna and Tripod
- Coax Cable to Connect Antenna to Here4 Base
- Laptop
- USB Cable to Connect to Flight Controller - both Micro USB and USB-C
- Travel Router/Wifi 
- Travel Router Battery Power
- Cellular Phone with Hotspot
- USB Charger
- Drone Battery Charger
- Sunglasses
- Bug Spray
- Small Folding Table
- Chair
- 4x4 sheet of plywood to field list for takeoff pad


# Field Tool List
- Hex Drivers – 2.5mm, 2mm, and 1.5mm
- Nut Drivers – 7mm, 5.5mm, 5mm
- Zip Ties
- Velcro
- Small Wire Cutters
- Wire Strippers
- Small Pliers
- #1 Phillips Screwdriver
- Flat Head Screwdriver
- Metric Ruler
- Cordless Drill
- Drill Bits

