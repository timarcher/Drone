# This script shows the basics of how to communicate with the ArduPilot flight controller.
# It prints out info from the flight controller. It assumes you have a HereLink Air Unit 
# at IP 192.168.144.10 and the Raspberry Pi can connect to it.
# It simply calls the read_telemetry function to print out several stats from the flight controller.

import sys
import time
import logging
import datetime
from logging.handlers import RotatingFileHandler
import signal
import traceback
import os
from pymavlink import mavutil

# Parameters for the script
connection_string = "udpout:192.168.144.10:14552"  # MAVLink connection string to the HereLink
baud_rate = 0

#connection_string = "udp:127.0.0.1:14553"           # MAVLink connection string to the local MavProxy
#baud_rate = 0

#connection_string = "/dev/ttyAMA0"                 # MAVLink connection string to the serial/UART connection
#baud_rate = 921600

# Ensure we are using MAVLink 2
os.environ["MAVLINK20"]='1'

# Configure logging to log to both file and system journal (stdout)
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for verbose output
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Logs to systemd journal (stdout)
        RotatingFileHandler(
            "gimbal_control.log",  # Log file name
            maxBytes=50 * 1024 * 1024,  # Max size per file: 50 MB
            backupCount=5  # Keep up to 5 backup files
        )
    ]
)

#
# Connect to drone
#
def connect(connection_string, baud_rate):
    logging.info(f"Connecting to {connection_string}")

    if baud_rate > 0:
        drone = mavutil.mavlink_connection(connection_string, baud=baud_rate, mavlink_version=2)
    else:
        drone = mavutil.mavlink_connection(connection_string, mavlink_version=2)

    drone.force_mavlink2 = True  # Ensure MAVLink2 is used

    # This workaround seems to be needed otherwise connections to the Herelink fail
    # waiting for the heartbeat
    drone.mav.ping_send(
        int(time.time() * 1e6), # Unix time in microseconds
        0, # Ping number
        0, # Request ping of all systems
        0 # Request ping of all components
    )

    drone.wait_heartbeat()
    logging.info(f"Heartbeat from system (system {drone.target_system} component {drone.target_component})")

    if drone.mavlink20():
        logging.info("MAVLink2 enabled.")
    else:
        logging.info("MAVLink1 detected (fallback).")

    return drone

#
# Generic helper function to send commands to the drone
#
def send_command_long(drone, command, param1=0, param2=0, param3=0, param4=0, param5=0, param6=0, param7=0):
    drone.mav.command_long_send(
        drone.target_system,    # target_system
        drone.target_component, # target_component
        command,                # command
        0,                      # confirmation
        param1, param2, param3, param4, param5, param6, param7
    )

#
# Helper function to set the rate at which specific MAVLink messages are sent.
#
def set_message_rate(drone, message_id, rate_hz):
    send_command_long(
        drone,
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
        message_id,
        1e6 / rate_hz,  # interval in microseconds
        0, 0, 0, 0, 0
    )

#
# Example function to parse telemetry data
#
def read_telemetry(drone):
    while True:
        msg = drone.recv_match(blocking=False)
        if not msg:
            continue

        # Print out the telemetry data
        # print(drone.recv_match().to_dict())        
        if msg.get_type() == 'ATTITUDE':
            logging.info(f"Pitch: {msg.pitch}, Roll: {msg.roll}, Yaw: {msg.yaw}")
        elif msg.get_type() == 'GLOBAL_POSITION_INT':
            logging.info(f"Lat: {msg.lat}, Lon: {msg.lon}, Alt: {msg.alt}")
        elif msg.get_type() == 'BATTERY_STATUS':
            voltage = msg.voltages[0] / 1000.0  # Voltage in volts
            remaining = msg.battery_remaining  # Remaining battery in percentage
            logging.info(f"Battery Voltage: {voltage:.2f}V, Remaining: {remaining}%")
        elif msg.get_type() == 'HEARTBEAT':
            # Extract flight mode
            mode = drone.flightmode
            # Extract arming status
            armed = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
            logging.info(f"Flight Mode: {mode}, Armed: {armed}")

        # Sleep to prevent flooding the console
        time.sleep(0.05)

#
# Helper function to close the connection to the drone
#
def close_connection(drone):
    logging.info("Closing connection to the drone...")
    drone.close()
    logging.info("Connection closed.")

#
# Signal handler function
#
def signal_handler(sig, frame, drone):
    logging.info(f"Received signal {sig}.")
    close_connection(drone)
    logging.info("Graceful shutdown completed.")
    exit(0)

#
# Main program logic
#
def main():

    drone = None

    try:
        logging.info(f"Simple Mavlink Test Script starting.")    

        drone = connect(connection_string, baud_rate)
        logging.info(f"Mavlink connection established to drone.")

        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, drone))
        signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame, drone))

        # Set message rates (example: 10 Hz for attitude and global position)
        set_message_rate(drone, mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 10)
        set_message_rate(drone, mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 10)
        set_message_rate(drone, mavutil.mavlink.MAVLINK_MSG_ID_BATTERY_STATUS, 1)
        set_message_rate(drone, mavutil.mavlink.MAVLINK_MSG_ID_HEARTBEAT, 1)

        # Start reading telemetry data
        read_telemetry(drone)

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        #traceback.print_exc()
        sys.exit(1)
    finally:
        logging.info(f"Script finished.")
        if drone:
            close_connection(drone)

if __name__ == "__main__":
    main()