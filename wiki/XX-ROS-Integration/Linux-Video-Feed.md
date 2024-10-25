# Install X server, GStreamer, and Video4Linux utilities. Stream a USB camera to the HDMI Port.
- Install packages needed:
```sh
sudo apt install xserver-xorg xinit x11-xserver-utils
sudo apt install lightdm
sudo apt install gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly
sudo apt install v4l-utils
sudo systemctl set-default graphical.target
```
- Ensure HDMI Output is setup:
```sh
sudo vi /boot/config.txt
```
Ensure these lines are in there:
```
hdmi_force_hotplug=1
hdmi_group=1
hdmi_mode=16
```
- Output video feed to the local HDMI port:
```sh
export DISPLAY=:0
gst-launch-1.0 v4l2src device=/dev/video0 ! videoconvert ! fbdevsink
```