This page contains details on performing the methodic configuration steps for the ArduPilot software on the drone.

# THIS PAGE IS INCOMPLETE AND A WORK IN PROGRESS

# YouTube Video
- [Hexacopter Drone Build Project – Part XX Methodic Configuration](https://youtu.be/XXX)
- [Hexacopter Drone Build Project – First Flight](https://www.youtube.com/watch?v=HhvRLNxARRs)

# Notes
- Read the blog post [How to methodically configure and tune any ArduCopter Blog Post](https://discuss.ardupilot.org/t/how-to-methodically-configure-and-tune-any-arducopter/110842) several times. It tooks me several reads before it really started to sink in.
- You may be in a hurry to skip steps you understand. Dont. This utility had me exploring areas of the documentation I have never read, and using tools I did not know existed. Think of it as a great structured classroom for learning how to tune your drone.
- Take the time to understand why each parameter is set the way it is.
- Here is how I configured the Notch Filters:
  - I did a hover test flying for about 50 seconds. Reviewed the logs in Mission Planner and got the average RPMs across all motors during a stable hover period. That was 2434. I divided by 60 to get 40.57. I set by base frequency to 41 then.
  - Open the log in the ArduPilot Filter Review tool. Highlight about 45 seconds of stable hover flight.
  - Set the amplitude scale to Linear. This is in the graph of Amplitude by Frequency.
  - Zoom in to the spikes so I can see them more clearly.
  - Set INS_HNTCH_FREQ to 41.
  - Then use the filter tool with as light a touch as possible, enabling as few harmonics with the lowest bandwidth and attenuation as reasonably flattens the noise peaks.
  - I did several test flights, and ultimately I was only able to enable the filter on the 1st harmonic as I had to select the option to enable it on all IMUs. When all IMUs were not selected the drone was very unstable. And with more harmonics selected than 1 and enabled on all IMUs the auto pilot would throw an error at boot.


# Supporting Materials
- [My Drones Methodic Configuration Directory](../../ardupilot-methodic-configurator/Hexacopter/) - This folder contains my methodic configuration. Use it for your own starting point.
- [ArduPilot Configuration](../ArduPilot-Config/ArduPilot-Config.md) - This page contains a consolidated list of the all of the configuration done in ArduPilot throughout the videos.

# References 
- [How to methodically configure and tune any ArduCopter Blog Post](https://ardupilot.github.io/MethodicConfigurator/TUNING_GUIDE_ArduCopter)
- [ArduPilot Methodic Configurator User Manual](https://github.com/ArduPilot/MethodicConfigurator/blob/master/USERMANUAL.md)
- [Methodic Configurator releases and downloads can be found here](https://github.com/ArduPilot/MethodicConfigurator/releases)
- [ArduPilot Web Tools](https://firmware.ardupilot.org/Tools/WebTools/)
- [ArduPilot Hardware Report Utility](https://firmware.ardupilot.org/Tools/WebTools/HardwareReport/)
- [ArduPilot Online Log Viewer](https://plotbeta.ardupilot.org/)
- [ArduPilot Filter Review Tool](https://firmware.ardupilot.org/Tools/WebTools/FilterReview/)
- [Follow the instructions from Peter Hall on his Blog Post to configure the Harmonic Notch filter(s)](https://discuss.ardupilot.org/t/new-fft-filter-setup-and-review-web-tool/102572).
- [ArduPilot MAGFit Tool](https://firmware.ardupilot.org/Tools/WebTools/MAGFit/)
- [QuikTune LUA Script Documentation and Scripts](https://ardupilot.org/copter/docs/quiktune.html)
- [Scripted MagFit flightpath generation](https://discuss.ardupilot.org/t/scripted-magfit-flightpath-generation/97536)
- [Downloading and Analyzing Data Logs in Mission Planner](https://ardupilot.org/copter/docs/common-downloading-and-analyzing-data-logs-in-mission-planner.html)