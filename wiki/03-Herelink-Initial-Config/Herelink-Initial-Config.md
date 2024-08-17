This page contains details on the initial unboxing and setup of the Herelink controller and air unit.


# YouTube Video
- [Hexacopter Drone Build Project – Part 3 Herelink Unboxing and Setup](https://youtu.be/6hCZ1OqMMvg)

# Notes
- Dont forget to set the time and time zone correctly on the controller.
- Be sure to enable video sharing in the Herelink controller.
- In the Joystick settings, 
  - Change the default channel for the wheel at the top from channel 5 to 16. This is because ArduPilot is setup for channel 5 to control flight modes.
  - Check the Wheel Acc setting
  - Reverse the hardwheel wheel as well so when you push it to the right it outputs a higher pulse on sbus out.
- Flight Mode Mapping
  - On the HereLink controller in the settings area, go to the buttons tab.
  - Map a short press of button A to channel 5. Set it to a toggle (T) button. Set default value to 1000, and active value to 2000. Then in Mission Planner go toi Setup->Flight Modes. You can then set Flight Mode 1 to Stabilize and Flight Mode 6 to Loiter.
  - Or here's anothes mapping example for more advanced and multiple flight mode mapping to support many modes:
    -  Flight Mode 1 - Loiter - PWM 0-1230 - Mapped to button A short press, active value 1100, mark as default button
    -  Flight Mode 2 - AutoTune - PWM 1231-1360 - Mapped to button A long press, active value 1300
    -  Flight Mode 3 - AltHold - PWM 1361-1490 - Mapped to button B short press, active value 1425
    -  Flight Mode 4 - Stabilize - PWM 1491-1620 - Mapped to button B long press, active value 1550
    -  Flight Mode 5 - RTL - PWM 1621-1749 - Mapped to button home short press, active value 1675
    -  Flight Mode 6 - Land - PWM 1750+ - Mapped to button home long press, active value 1800
- In Mission Planner go to the Setup->FailSafe tab. Configure the radio failsafe to Enabled always RTL, and an FS Pwm of 975
- In Mission Planner you can also go to the Config->User Params tab and map actions to other channels. For example you could map channel 7 to fence enable/disable. This would be the same as setting RC7_OPTION to a value of 11. Other fun things, for example, you could map it to the lost copter sound.


# References 
## Herelink User Guides
- User guides for the Herelink [can be found here](https://docs.cubepilot.org/user-guides/herelink/herelink-user-guides).
- Many thanks to Painless360 for their video which gave me the info needed to perform this process. Be sure to [watch their video here](https://www.youtube.com/watch?v=DVPRaErKsn0&t=2167s).