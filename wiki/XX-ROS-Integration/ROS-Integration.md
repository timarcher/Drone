# THIS PAGE IS INCOMPLETE AND A WORK IN PROGRESS

This page contains details on installing ROS2 on the Raspberry PI and integrating it with the flight controller.

# YouTube Video
- [Hexacopter Drone Build Project – Part XX ROS Integration](https://youtu.be/XXX)

# Notes
- Make sure you have a Raspberry Pi with Ubuntu 24.04 installed on it first. See the [Onboard-Computer-and-Ethernet](../10-Onboard-Computer-and-Ethernet/Onboard-Computer-and-Ethernet.md) page and associated video if you havent done that yet.
ros

# ROS2 Installation Notes
- Follow the instructions to install ROS2 on your Raspberry Pi by following the guide for [Installing ROS2 on Ubuntu 24.04](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html). I installed the Recommended Desktop Install wehich includes ROS, RViz, demos, tutorials. You need this to run the talker/listener demo in the install instructions.
- Edit ~/.bashrc to add the following line to it so your ROS environment is configured every time you login:
```sh
source /opt/ros/jazzy/setup.bash
```
- Install MAVROS for ROS 2 to use ROS 2 to read a MAVLink stream:
```sh
sudo apt install ros-jazzy-mavros ros-jazzy-mavros-extras
```
- Install the geopgraphic lib
```sh
wget https://raw.githubusercontent.com/mavlink/mavros/master/mavros/scripts/install_geographiclib_datasets.sh
sudo bash ./install_geographiclib_datasets.sh
```
- Verify the geographic lib installation:
```sh
ls /usr/share/GeographicLib/geoids/
# You should see the egm96-5.pgm file, among others, in this directory.
```

# Starting MAVROS
MAVROS is a ROS package that allows users to control drones using the MAVLink protocol. MAVROS can convert between ROS topics and MAVLink messages, allowing ArduPilot vehicles to communicate with ROS.
On the Raspberry Pi, run the following command to start the MAVROS bridge. This command launches the MAVROS node with the specified configuration, connecting to the Herelink Air Unit at 192.168.144.10 via UDP on port 14552 and setting up a Ground Control Station (GCS) URL for communication.
```sh
ros2 launch mavros apm.launch fcu_url:=udp://:14552@192.168.144.10 gcs_url:=udp://@
```

In another SSH window you should now be able to see the nodes and topics by running these commands:
```sh
ros2 node list
ros2 topic list
```

You can print out the messages about your battery health with this command:
```sh
ros2 topic echo /mavros/battery
```

Print out the current flight mode with this command:
```sh
ros2 topic echo /mavros/state
```


# Supporting Materials
- [ArduPilot Configuration](../ArduPilot-Config/ArduPilot-Config.md) - This page contains a consolidated list of the all of the configuration done in ArduPilot throughout the videos.

# References 
- [Installing ROS2 Jazzy on Ubuntu 24.04](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)

