This directory contains a script showing how to use mavlink to connect to a HereLink and send instructions to the flight controller.
It will attempt to:
- Arm the drone.
- Takeoff to a height of 3 meters.
- Read telemetry for 10 seconds and print to the screen.
- Land the drone.


To setup this script, you must do the following:
1. Make a directory to hold the scripts.
```sh
mkdir ~/drone_scripts
cd ~/drone_scripts
```
1. Copy the files to your linux machine into the diorectry ~/drone_scripts: requirements.txt and log_downloader.py
2. Setup your Python environment.
```sh
sudo apt update
sudo apt install python3-pip

python3 -m venv drone_scripts_env
source drone_scripts_env/bin/activate
pip3 install -r requirements.txt
```
3. Copy the script to your linux machine and execute it:
```sh
python3 sample02_command_examples.py
```