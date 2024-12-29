This directory contains a script to turn on and off the neopixel LEDs through RC Channel 6.
When that channel goes high, the LED scanning pattern will be enabled. When low, it will be turned off.

To setup this script, you must do the following:
1. Make a directory to hold the scripts.
```sh
mkdir ~/drone_scripts
cd ~/drone_scripts
```
2. Copy the files to your linux machine into the diorectry ~/drone_scripts: requirements.txt and monitor_channel_to_enable_leds.py
3. Setup your Python environment.
```sh
sudo apt update
sudo apt install python3-pip

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
sudo vi /etc/systemd/system/led_monitor.service
```

Add the following content, replacing placeholders with actual paths:
```sh
[Unit]
Description=Monitor MAVLink channel and control LED strip
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/drone_scripts
ExecStartPre=/bin/sleep 5
ExecStart=/home/ubuntu/drone_scripts/drone_scripts_env/bin/python3 /home/ubuntu/drone_scripts/monitor_channel_to_enable_leds.py
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
sudo systemctl enable led_monitor.service
```

7. To test the service immediately, run:
```sh
sudo systemctl start led_monitor.service
```

8. Check its status to ensure it’s running:
```sh
sudo systemctl status led_monitor.service
```

9. Reboot and ensure the service is running then after the reboot:
```sh
sudo reboot
sudo systemctl status led_monitor.service
```

10. To debug issues, check the logs:
```sh
journalctl -u led_monitor.service -f
```