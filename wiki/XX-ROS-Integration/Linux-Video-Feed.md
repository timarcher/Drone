# Install X server, GStreamer, and Video4Linux utilities. Stream a USB camera to the HDMI Port.
- First ensure you have ubuntu desktop installed.
- Install packages needed:
```sh
sudo apt update
sudo apt install -y ffmpeg gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly
sudo apt install -y v4l-utils
sudo apt install -y fbset
sudo apt install -y gstreamer1.0-libcamera
```
- Stop the Login Screen Service
```sh
sudo systemctl stop display-manager
```
- Set the framebuffer output format
```sh
sudo fbset -xres 1024 -yres 768 -depth 16
```
- Automatically Switch to the Correct TTY
Ensure the system is on a TTY console and not stuck on an X session or Wayland. If necessary, switch to TTY1 using:
```sh
sudo chvt 1
```
- Diplay video formats supported by the camera:
```sh
sudo v4l2-ctl --list-formats-ext -d /dev/video4
```
- Output video feed to the local HDMI port:
```sh
sudo gst-launch-1.0 v4l2src device=/dev/video4 ! videoconvert ! fbdevsink
```
OR
```sh
sudo ffmpeg -f v4l2 -video_size 1280x720 -framerate 15 -i /dev/video4 -pix_fmt rgb565le -f fbdev /dev/fb0
```
- Revert to Normal After Use
```sh
sudo systemctl start display-manager
```

# Use Gstreamer to Broadcast to VLC Media Player
- On the linux machine run command:
```
sudo gst-launch-1.0 v4l2src device=/dev/video4 ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! mpegtsmux ! udpsink host=IP_OF_MACHINE_TO_STREAM_TO port=5000
```
- And on the PC running VLC media player do Media > Open Network Stream, and then enter udp://@:5000

# Use Gstreamer to Stream To Mission Planner on Another PC
- On the linux machine run command:
```
sudo gst-launch-1.0 v4l2src device=/dev/video4 ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! rtph264pay config-interval=1 pt=96 ! udpsink host=<MISSION_PLANNER_COMPUTER_IP> port=5600
```
An alternative if have a raspberry pi CSI camera is to use libcamerasrc:
```
gst-launch-1.0 libcamerasrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! rtph264pay config-interval=1 pt=96 ! udpsink host=puter port=5600
```

You can also use the tee command to send to multiple computers:
```
gst-launch-1.0 libcamerasrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! rtph264pay config-interval=1 pt=96 ! tee name=t \
  t. ! queue ! udpsink host=tims-pc01 port=5600 \
  t. ! queue ! udpsink host=puter port=5600
```

- Mission planner might automatically pick up the video feed when it is started. But if not, right click on the HUD display > Video > Set Gstreamer Source. Enter this in there:
```
udpsrc port=5600 ! application/x-rtp, encoding-name=H264, payload=96 ! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink
```



# Setup a Lightweight RTSP Server on the Linux Machine
- Download a lightweigth RTSP server and install it:
```
mkdir ~/rtsp
cd ~/rtsp
wget https://github.com/bluenviron/mediamtx/releases/download/v1.12.0/mediamtx_v1.12.0_linux_amd64.tar.gz
tar -zxpvf mediamtx_v1.12.0_linux_arm64v8.tar.gz
./mediatx
```
- Use ffmpeg to send your video to the server
```
ffmpeg -f v4l2 -i /dev/video4 -vcodec libx264 -preset ultrafast -tune zerolatency -f rtsp rtsp://localhost:8554/mystream
```
- Now connect to the stream
  - From VLC: rtsp://<your-linux-pc-ip>:8554/mystream
  - From Mission Planner: rtspsrc location=rtsp://<your-linux-pc-ip>:8554/mystream latency=0 ! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink

# Use OpenCV to Display to the HDMI Port
- Install dependencies:
```sh
sudo apt install python3-opencv python3-pillow
```
- Run python program
```python3
```