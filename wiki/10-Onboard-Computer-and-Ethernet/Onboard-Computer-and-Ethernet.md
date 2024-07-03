This page contains details on the installation of a Raspberry Pi 5 companion computer and the setup of a BotBlox SwitchBlox Ethernet switch to create a network onboard the drone.

# YouTube Video
- [Hexacopter Drone Build Project – Part 10 Onboard Computer and Ethernet](https://www.youtube.com/XXX)

# Notes
- 192.168.43.1 is HereLink controller IP address when you connect to it through it's WiFi access point mode from a ground control station (i.e., a laptop or computer).
- There is no dhcp provided by the HereLink Air Units. You need to manual set an ip address inside the range eg 192.168.144.0, subnet mask 255.255.255.0. For example, use 192.168.144.50. This will put you within the ip range of the airunit and gcs unit, so they are accessible from the airunit ethernet port.
  - The Airunit and Controller occupy the addresses 192.168.144.10 and 192.168.144.11, so you cannot use these IP addresses for other devices on the network within the drone.
  - HereLink Air Unit is at IP address 192.168.144.10
  - HereLink Controlleris at IP address 192.168.144.11
- You can get rtsp video from 192.168.43.1, 192.168.144.10, or 192.168.144.11
- You can get mavlink from 192.168.43.1, 192.168.144.10, or 192.168.144.11 port 14552
- To be able to route traffic between the Drone Network and the Ground Control Station HereLink WiFi AP:
  - GCS/Laptop needs a static route to 192.168.144.0/24 via 192.168.43.1
    - To do this, assuming your GCS is a Windows PC, open a command prompt as administrator and run `route add 192.168.144.0 mask 255.255.255.0 192.168.43.1`
    - To make the route persistent across reboots, run it with the -p flag: `route -p add 192.168.144.0 mask 255.255.255.0 192.168.43.1`
  - Companion computer needs a static route for 192.168.43.0/24 via 192.168.144.11
    - To do this temporarily, run the command: `sudo ip route add 192.168.43.0/24 via 192.168.144.11`
    - To do it permanently, simply leave in the routes section in the static IP configuration as shown below.
- URL for the RTSP video stream is: rtsp://192.168.43.1:8554/fpv_stream or rtsp://192.168.144.11:8554/fpv_stream

# Setting An IP Address on the Raspberry Pi
The following commands will give your Raspberry Pi a static IP address that will allow it to communicate with the HereLink Air Unit, Controller, and the Ground Control Station (if connected through the WiFi AP on the HereLink controller). 

- Open the Netplan configuration file for editing: `sudo vi /etc/netplan/01-netcfg.yaml`
- Edit the configuration file to set the static IP address. The file should look something like this
```
network:
  version: 2
  ethernets:
    eth0:
      addresses:
        - 192.168.144.55/24
      dhcp4: no
      routes:
        - to: 192.168.43.0/24
          via: 192.168.144.11
```
- After saving the file, apply the Netplan configuration with the following command: `sudo netplan apply`
- Verify the configuration. You can check the IP address assignment by using the ip command: `ip addr show eth0`

# Python and Pymavlink
You may wish to interact with your drone from your companion computer using Python. This section shows the basics of how to communicate with the ArduPilot flight controller.

- [Pymavlink](https://github.com/ArduPilot/pymavlink) is a Python library for generating and parsing MAVLink messages. MAVLink (Micro Air Vehicle Link) is a communication protocol used primarily in drone applications for telemetry and command/control communication.


1. Install dependencies: `sudo apt update && sudo apt install python3-full python3-pip python-is-python3`
1. Create a python virtual environment: `python3 -m venv drone01`
1. Activate virtual environment: `source drone01/bin/activate`
2. Install python libraries into the virtual environment: `pip3 install pymavlink`
3. Try a simple test program to communicate with the flight controller. Create a file named `sample01_simple_mavlink_test.py` and add the contents of [this file](../../src/sample01_simple_mavlink_test/sample01_simple_mavlink_test.py) to it.
4. Run the program: `python sample01_simple_mavlink_test.py`
5. Deactivate the virtual environment: `deactivate`
6. Delete the virtual environment: `rm -rf drone01`



# Supporting Materials
- [Raspberry Pi Imager](https://www.raspberrypi.com/software/) - Download and install the Raspberry Pi Imager from this website.
- [PuTTY SSH Client](https://www.putty.org/) - Free SSH client you can use to connect to your Raspberry Pi.
- [VLC Media Player](https://www.videolan.org/) - Used to view RTSP video streams over a network connection.
- [ArduPilot Configuration](../ArduPilot-Config/ArduPilot-Config.md) - This page contains a consolidated list of the all of the configuration done in ArduPilot throughout the videos.

# References 
- Herelink air unit to botblox switch wiring is shown [on this page](https://ardupilot.org/copter/docs/common-ethernet-vehicle.html).
- ArduPilot discussion post on Ethernet Connected Ardupilot Vehicle Example [can be found here](https://discuss.ardupilot.org/t/ethernet-connected-ardupilot-vehicle-example/117942).