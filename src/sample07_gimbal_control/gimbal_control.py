# This script will automatically download logs from the flight controller.
# It assumes you have a HereLink Air Unit at IP 192.168.144.10 and the Raspberry Pi can connect to it.

import sys
import time
import signal
import logging
import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
import time
import json
from pymavlink import mavutil

# Parameters for the script
#connection_string = "udpout:192.168.144.10:14552"  # MAVLink connection string to the HereLink
#baud_rate = 0

connection_string = "udp:127.0.0.1:14553"           # MAVLink connection string to the local MavProxy
baud_rate = 0

#connection_string = "/dev/ttyAMA0"                 # MAVLink connection string to the serial/UART connection
#baud_rate = 921600

log_output_directory = "/home/ubuntu/drone_logs"    # Where logs will be downloaded to

loop_sleep_time_seconds = 300                       # Script will wake up every this many seconds and check for logs to download

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

    # Wait for a response (blocking) to the MAV_CMD_SET_MESSAGE_INTERVAL command and print result
    response = drone.recv_match(type='COMMAND_ACK', blocking=True)
    if response and response.command == mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL and response.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        logging.info(f"set_message_rate command accepted. {response}")
    else:
        logging.info(f"set_message_rate command failed. {response}")


#
# set_gimbal_pitch_yaw
#
def set_gimbal_pitch_yaw(connection, pitch_degrees=0, yaw_degrees=0):
    # Define gimbal control parameters
    target_system = connection.target_system  # Target system ID (usually 1 for the first connected system - the flight controller)
    target_component = mavutil.mavlink.MAV_COMP_ID_GIMBAL  # Use the correct component ID for gimbal

    logging.info(f"Target system: {target_system}, Target component: {target_component}")

    # Control the gimbal pitch and yaw using MAV_CMD_DO_GIMBAL_MANAGER_PITCHYAW
    pitch = pitch_degrees  # degrees
    yaw = yaw_degrees  # degrees

    logging.info(f"Sending gimbal control command to set yaw to {yaw} degrees")

    connection.mav.command_long_send(
        target_system, target_component,
        mavutil.mavlink.MAV_CMD_DO_GIMBAL_MANAGER_PITCHYAW, 0,
        pitch,  # Pitch angle in degrees
        yaw,    # Yaw angle in degrees
        float('nan'),  # Pitch rate (NaN to signal unset)
        float('nan'),  # Yaw rate (NaN to signal unset)
        0, 0, 0
    )

    # Wait for a response (blocking) to the MAV_CMD_DO_GIMBAL_MANAGER_PITCHYAW command and print result
    response = connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=5)
    if response:
        logging.info(f"Received COMMAND_ACK: {response}")
        if response.command == mavutil.mavlink.MAV_CMD_DO_GIMBAL_MANAGER_PITCHYAW and response.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            logging.info(f"Gimbal yaw set to {yaw} degrees: {response}")
        else:
            logging.error(f"Failed to set gimbal yaw: {response}")
            # Check if the gimbal is actually moving to the desired position
            # gimbal_status = connection.recv_match(type='GIMBAL_MANAGER_STATUS', blocking=True, timeout=5)
            # if gimbal_status and gimbal_status.yaw == yaw:
            #     logging.info(f"Gimbal yaw successfully set to {yaw} degrees despite error message.")
            # else:
            #     logging.error(f"Gimbal yaw not set to {yaw} degrees.")
    else:
        logging.error("No response received for MAV_CMD_DO_GIMBAL_MANAGER_PITCHYAW")

#
# log_gimbal_device_information
#
def log_gimbal_device_information(connection):
    # Request gimbal status
    gimbal_device_info = connection.recv_match(type='GIMBAL_DEVICE_INFORMATION', blocking=True, timeout=10)
    logging.info(f"Received GIMBAL_DEVICE_INFORMATION: {gimbal_device_info}")
    if gimbal_device_info:
        logging.info(f"Gimbal Status - Vendor Name: {gimbal_device_info.vendor_name}, Model Name: {gimbal_device_info.model_name}, Firmware Version: {gimbal_device_info.firmware_version}")
    else:
        logging.error("No response received for GIMBAL_DEVICE_INFORMATION")

#
# Main program logic
#
def main():
    drone = None

    try:
        logging.info(f"Gimbal Control Script starting.")

        drone = connect(connection_string, baud_rate)
        logging.info(f"Mavlink connection established to drone.")

        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, drone))
        signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame, drone))

        # Set the rate for LOG_DATA to 5 Hz
        #logging.info(f"Setting message rate: {mavutil.mavlink.MAVLINK_MSG_ID_LOG_DATA}")
        #set_message_rate(drone, mavutil.mavlink.MAVLINK_MSG_ID_LOG_DATA, 50)

        #logging.info(f"Setting message rate: {mavutil.mavlink.MAVLINK_MSG_ID_GIMBAL_DEVICE_INFORMATION}")
        #set_message_rate(drone, mavutil.mavlink.MAVLINK_MSG_ID_GIMBAL_DEVICE_INFORMATION, 1)
        
        log_gimbal_device_information(drone)

        
        set_gimbal_pitch_yaw(drone, 0, 0)
        time.sleep(3)

        set_gimbal_pitch_yaw(drone, 5, 45)
        time.sleep(3)

        set_gimbal_pitch_yaw(drone, -5, -45)
        time.sleep(3)

        set_gimbal_pitch_yaw(drone, 0, 0)
        time.sleep(3)

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