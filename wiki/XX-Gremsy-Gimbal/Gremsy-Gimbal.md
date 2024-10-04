This page contains details on setting up the Gremsy T7 Gimbal with the drone.

# YouTube Video
- [Hexacopter Drone Build Project – Part XX Gremsy T7 Gimbal](https://youtu.be/XXX)

# Notes
- I replaced the stock 12mm payload carbon fiber tubes that came with the drone with longer 330mm ones from Amazon.
- I bought a longer 6-Pin JST-GH Twisted Pair - MRC0212 - 1000mm length cable from 3DR in order to make the serial connection from the gimbal to the Kore carrier board. Its a 6 pin connector and wire designed for I2C, but I removed 3 wires and swapped TX/RX on one end to make it work for the gimbal.
- Ensure you load the latest firmware, 7.7.1 or later! Download from https://github.com/Gremsy/T7-Firmware/releases
  - NOTE: Gyro MUST be calibrated after upgrading completely.
    Open gTune --> SETTINGS --> GYRO --> CALIBRATE
    NOTE: Users should load the recommended gimbal parameters and perform an AUTO-TUNE process.
    Open gTune --> SETTINGS --> STIFFNESS --> AUTOTUNE
- Tuning the stiffness: Increase the stiffness setting 5-10 points at a time until oscillation appears then reduce 5 points until oscillation subsides. Slowly increase this setting until you feel an oscillation in the tilt axis, then reduce the setting until the oscillation subsides.
  - I have my settings at: Tilt 30, Roll 35, Pan 50. Gyro Filter 2, and Output Filter 3
- The gimbal serial connection gets connected to the Telemetry 2 port on the Kore carrier board. See [this page for the wiring diagram](https://ardupilot.org/copter/docs/common-gremsy-pixyu-gimbal.html).
- In the Gremsy GTuneDesktop app, change these options:
  - Settings -> Controls -> Mavlink - Set to enabled
  - Also go to the settings button in top left under mode, and unselect the "Reduce Drift by Drone" option, Pan Axis will be disabled.
- To control the gimbal on the Herelink controller:
  - Ensure you install the latest QGroundControl release for the Herelink: [QGroundControl Herelink Releases](https://github.com/CubePilot/qgroundcontrol-herelink/releases)
  - Then follow [these instructions on Youtube](https://www.youtube.com/watch?v=a-cLzYD7HBk&t=43s) to install the custom APK file for QGroundControl on the Herelink.

# Supporting Materials
- [ArduPilot Configuration](../ArduPilot-Config/ArduPilot-Config.md) - This page contains a consolidated list of the all of the configuration done in ArduPilot throughout the videos.

# References 
- [Gremsy T7 Firmware](https://gremsy.com/support/product-support/series-gremsy-t-s/gremsy-t7/gremsy-t7-download)
- [Ardupilot to Gremsy HDMI Quick Release Wiring](https://ardupilot.org/copter/docs/common-gremsy-pixyu-gimbal.html)
- [Gremsy GTune Desktop Software](https://github.com/Gremsy/gTuneDesktop/releases)