This directory contains information on using Tailscale to access the Raspberry Pi remotely through a VPN.


# Install Tailscale On The Linux Machine
1. Download and install
```sh
sudo apt install tailscale -y
#or
#curl -fsSL https://tailscale.com/install.sh | sudo sh
```
2. Enable IP forwarding on the linux machine. This will allow you to access other devices on it's network as well, such as the herelink. This command below was for Ubuntu 24.04:
```sh
sudo sysctl -w net.ipv4.ip_forward=1
```
3. Run the following to start Tailscale. It will print out a URL to open in your browser and sign into Tailscale with. Connect it to your Tailnet. This also assumes your Linux machine has an IP address on the 192.168.144.0 network.
```sh
sudo tailscale up --advertise-routes=192.168.144.0/24 --accept-routes
```
4. Go to the [Tailscale Admin Panel](https://login.tailscale.com/admin/machines) and approve the route to 192.168.144.0/24. You will need to click on the linux machine, go to its details, and approve in that section.


# Setup Tailscale On A Second Device (i.e., Windows):
1. Install Tailscale on the windows machine by downloading and isntalling the software from: https://tailscale.com/download/windows
2. Login when prompted


# Access your machines in the Tailscale browser interface
1. View your connected devices at this URL: https://login.tailscale.com/admin/machines

# Access Drone Via MavProxy
1. Have both a windows machine with tailscale on it and your raspberry pi on the drone conencted to the same Tailnet.
2. Ensure you have Mavproxy running on your drone, configured to send UDP traffic to the IP address of the windows PC:
/home/ubuntu/drone_scripts/drone_scripts_env/bin/mavproxy.py --master=/dev/ttyAMA0 --baudrate 921600 --out=udp:100.111.69.17:14555 --cmd="set flushlogs True" --state-basedir="/home/ubuntu/drone_scripts" --logfile=mav.tlog --daemon
3. In mission planner, connect via UDP and when prompted for the port enter 14555.


# Acces Drone Through the Herelink
Assuming you have your Linux machine connected to the same Ethernet network with your Herelink Air Unit, you should be able to connect to it then:
1. From the windows machine, try to access the Herelink Air Unit RTSP stream by opening VLC Media Player and going to: rtsp://192.168.144.10:8554/H264Video

# Removing Tailscale
```sh
sudo tailscale logout
sudo tailscale down
sudo apt remove tailscale
```
