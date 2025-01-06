This directory contains a script to interact with the gimbal attached to the drone.

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
