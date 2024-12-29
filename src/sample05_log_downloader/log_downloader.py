# This script will automatically download logs from the flight controller.
# It assumes you have a HereLink Air Unit at IP 192.168.144.10 and the Raspberry Pi can connect to it.

import time
import signal
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
import time
from pymavlink import mavutil

# Parameters for the script
#connection_string = "udpout:192.168.144.10:14552"  # MAVLink connection string to the HereLink
#baud_rate = 0

connection_string = "udp:127.0.0.1:14550"           # MAVLink connection string to the local MavProxy
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
            "log_downloader.log",  # Log file name
            maxBytes=50 * 1024 * 1024,  # Max size per file: 50 MB
            backupCount=5  # Keep up to 5 backup files
        )
    ]
)

#
# Connect to drone
#
def connect(connection_string, baud_rate):
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

#
# Determine if the drone is disarmed
#
def is_drone_disarmed(connection):
    """Check if the drone is disarmed."""
    msg = connection.recv_match(type='HEARTBEAT', blocking=True, timeout=5)
    if msg:
        return msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED == 0
    return False

#
# Download a log file from the flight controller
#
def download_log(connection, log, log_filename):
    """Download a log using MAVLink2."""
    try:

        log_filename_tmp = f"{log_filename}.tmp"

        # Check if MAVLink2 is enabled
        #if not connection.mavlink20():
        #    raise RuntimeError("MAVLink2 is required for faster downloads. Ensure MAVLink2 is enabled.")

        logging.info(f"Downloading log ID {log.id} ({log.size} bytes)...")
        start_offset = 0
        bytes_received = 0
        chunk_size = 1024  # Maximum safe payload size for MAVLink2 LOG_DATA
        
        chunks_downloaded = 0
        with open(log_filename_tmp, "wb") as log_file:
            while start_offset < log.size:
                # Check if the drone becomes armed during the download
                if chunks_downloaded % 100 == 0:
                    if not is_drone_disarmed(connection):
                       raise Exception("Drone became armed. Stopping log download.")

                # Request the next chunk of the log
                connection.mav.log_request_data_send(
                    target_system=connection.target_system,
                    target_component=connection.target_component,
                    id=log.id,
                    ofs=start_offset,
                    count=chunk_size
                )

                # Wait for LOG_DATA message
                msg = connection.recv_match(type='LOG_DATA', blocking=True, timeout=2)
                if not msg:
                    logging.warning(f"Timeout waiting for log data at offset {start_offset}. Retrying...")
                    continue

                # Write the received data to the file
                log_file.write(bytes(msg.data))
                start_offset += len(msg.data)
                bytes_received += len(msg.data)
                chunks_downloaded += 1

                # Logging progress
                if chunks_downloaded % 100 == 0:
                    percent_complete = (bytes_received / log.size) * 100
                    logging.info(f"Log {log.id}: {bytes_received} / {log.size} bytes ({percent_complete:.2f}% complete)")

        # Final percent complete message
        percent_complete = (bytes_received / log.size) * 100
        logging.info(f"Log {log.id}: {bytes_received} / {log.size} bytes ({percent_complete:.2f}% complete)")

        # If the log file already exists, then remove it before we rename the temporary file
        # just downloaded to the log filename
        if Path(log_filename).exists():
            Path(log_filename).unlink()

        # Rename the file from the temporary file name
        os.rename(log_filename_tmp, log_filename)

        logging.info(f"Log {log.id} downloaded successfully to {log_filename}.")

    except Exception as e:
        logging.error(f"Error downloading log {log.id}: {e}", exc_info=True)
        try:
            if Path(log_filename_tmp).exists():
                Path(log_filename_tmp).unlink()            

            if Path(log_filename).exists():
                Path(log_filename).unlink()
        except Exception as cleanup_error:
            logging.error(f"Error deleting partial log file {log_filename}: {cleanup_error}", exc_info=True)

#
# Download all the logs from the flight controller
#
def download_logs(connection):
    """Download finished logs."""

    # Check if the is armed, if so dont do the download
    if not is_drone_disarmed(connection):
        logging.info("Drone is armed. No logs will be downloaded.")
        return

    logging.info("Drone is disarmed. Checking to see if any logs need to be downloaded.")

    # Request a list of available logs
    connection.mav.log_request_list_send(
        target_system=connection.target_system,
        target_component=connection.target_component,
        start=0,
        end=0xFFFF
    )

    logs = []

    # Receive LOG_ENTRY messages
    while True:
        msg = connection.recv_match(type='LOG_ENTRY', blocking=True, timeout=5)
        if not msg:
            break
        logs.append(msg)
        logging.info(f"Log ID: {msg.id}, Size: {msg.size}, TimeUTC: {msg.time_utc}, NumLogs: {msg.num_logs}, LastLogNum: {msg.last_log_num}")

    # Filter logs (e.g., skip the latest ongoing log)
    # (Logic is removed for now)
    finished_logs = [log for log in logs]

    if not finished_logs:
        logging.info("No finished logs are available for download.")
        return

    # Download logs
    for log in finished_logs:
        # Check if the drone becomes armed during the download
        if not is_drone_disarmed(connection):
           raise Exception("Drone became armed. Stopping log download.")

        # Check if the log file already exists
        log_filename = f"{log_output_directory}/log_{log.id}.bin"
        if Path(f"{log_filename}").exists():
            # See if the log file is the same size in bytes
            local_log_file_size = os.path.getsize(log_filename)
            if local_log_file_size == msg.size:
                logging.info(f"Log ID {log.id} already exists. Skipping download.")
                continue
            else:
                logging.info(f"Log ID {log.id} already exists but file sizes are different. File will be downloaded and the local log file overwritten.")

        download_log(connection, log, log_filename)


#
# Main program logic
#
def main():
    logging.info(f"Log Download Script starting.")

    while True:
        logging.info(f"About to check if there are new logs to download.")

        drone = connect(connection_string, baud_rate)
        logging.info(f"Mavlink connection established to drone.")

        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, drone))
        signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame, drone))

        # Set the rate for LOG_DATA to 5 Hz
        #logging.info(f"Setting message rate: {mavutil.mavlink.MAVLINK_MSG_ID_LOG_DATA}")
        #set_message_rate(drone, mavutil.mavlink.MAVLINK_MSG_ID_LOG_DATA, 50)

        try:
            Path(f"{log_output_directory}").mkdir(parents=True, exist_ok=True)
            download_logs(drone)
        except Exception as e:
            logging.error(f"An error occurred: {e}", exc_info=True)
            #traceback.print_exc()
        finally:
            close_connection(drone)

        logging.info(f"Finished processing logs. Script will now sleep for {loop_sleep_time_seconds} seconds.")
        time.sleep(loop_sleep_time_seconds)

    logging.info(f"Log Download Script finished.")


if __name__ == "__main__":
    main()