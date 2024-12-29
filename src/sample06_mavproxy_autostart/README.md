This directory contains instructions for how to autostart mavproxy when the system boots.

To setup this script, you must do the following:
1. Make a directory to hold the scripts.
```sh
mkdir ~/drone_scripts
cd ~/drone_scripts
```
2. Copy the files to your linux machine into the diorectry ~/drone_scripts: requirements.txt and mavproxy.py
3. Setup your Python environment.
```sh
sudo apt update
sudo apt install python3-pip

# If you dont remove modemanager you'll get WARNING: You should uninstall ModemManager as it conflicts with APM and Pixhawk
sudo apt remove modemmanager

python3 -m venv drone_scripts_env
source drone_scripts_env/bin/activate
pip3 install -r requirements.txt
```
4. Determine the absolute path of the Python interpreter in your environment: 
```sh
which python3
```
5. Create a Systemd Service File to auto start the script:
```sh
sudo vi /etc/systemd/system/mavproxy.service
```

Add the following content, replacing placeholders with actual paths:
```sh
[Unit]
Description=MAVProxy Autostart
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/drone_scripts
ExecStartPre=/bin/sleep 3
ExecStart=/home/ubuntu/drone_scripts/drone_scripts_env/bin/mavproxy.py --master=/dev/ttyAMA0 --baudrate 921600 --out=udp:127.0.0.1:14550 --cmd="set flushlogs True" --state-basedir="/home/ubuntu/drone_scripts" --logfile=mav.tlog --console --daemon
Restart=on-failure
TimeoutStartSec=30
Environment="PATH=/home/ubuntu/drone_scripts/drone_scripts_env/bin/python3:/usr/bin:/bin"
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

6. Reload Systemd and Enable the Service
```sh
sudo systemctl daemon-reload
sudo systemctl enable mavproxy.service
```

7. To test the service immediately, run:
```sh
sudo systemctl start mavproxy.service
```

8. Check its status to ensure it’s running:
```sh
sudo systemctl status mavproxy.service
```

9. Reboot and ensure the service is running then after the reboot:
```sh
sudo reboot
sudo systemctl status mavproxy.service
```

10. To debug issues, check the logs:
```sh
journalctl -u mavproxy.service -f
```