This page contains details on setting up the Gremsy T7 Gimbal with the drone.

# YouTube Video
- [Hexacopter Drone Build Project – Part XX Gremsy T7 Gimbal](https://youtu.be/XXX)

# Notes
- I replaced the stock 12mm payload carbon fiber tubes that came with the drone with longer 330mm ones from Amazon.
- I bought a longer 6-Pin JST-GH Twisted Pair - MRC0212 - 1000mm length cable from 3DR in order to make the serial connection from the gimbal to the Kore carrier board. Its a 6 pin connector and wire designed for I2C, but I removed 3 wires and swapped TX/RX on one end to make it work for the gimbal.
- The gimbal serial connection gets connected to the Telemetry 2 port on the Kore carrier board. See [this page for the wiring diagram](https://ardupilot.org/copter/docs/common-gremsy-pixyu-gimbal.html).


# Supporting Materials
- [ArduPilot Configuration](../ArduPilot-Config/ArduPilot-Config.md) - This page contains a consolidated list of the all of the configuration done in ArduPilot throughout the videos.

# References 
- [Gremsy T7 Firmware](https://gremsy.com/support/product-support/series-gremsy-t-s/gremsy-t7/gremsy-t7-download)
- [Ardupilot to Gremsy HDMI Quick Release Wiring](https://ardupilot.org/copter/docs/common-gremsy-pixyu-gimbal.html)
- [Gremsy GTune Desktop Software](https://github.com/Gremsy/gTuneDesktop/releases)