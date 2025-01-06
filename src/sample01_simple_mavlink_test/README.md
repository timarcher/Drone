This directory contains a script showing how to use mavlink to connect to a HereLink and read telemetry from it.

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
python3 sample01_simple_mavlink_test.py
```