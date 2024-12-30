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

connection_string = "udp:127.0.0.1:14554"           # MAVLink connection string to the local MavProxy
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
# Determine if the drone is disarmed
#
def is_drone_disarmed(connection):
    """Check if the drone is disarmed."""
    max_retries = 5
    retries = 0
    while retries < max_retries:
        msg = connection.recv_match(type='HEARTBEAT', blocking=True, timeout=5)
        if msg:
            #logging.info(f"Checking if drone is disarmed. base_mode: {msg.base_mode} MAV_MODE_FLAG_SAFETY_ARMED: {mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED} - Logic check: {msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED}.")
            return msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED == 0

        retries += 1
        logging.info(f"Checking if the drone is disarmed. Attempt {retries} timed out. No HEARTBEAT received. Retrying...")
        time.sleep(1)  # Sleep for 1 second before retrying

    logging.info(f"Timeout occurred checking is drone is disarmed. Assuming drone is armed.")
    return False

#
# Read the download status file
#
def read_download_status_file(json_file):
    """Read progress from the JSON file."""
    if not Path(json_file).exists():
        return 0, 0  # Default values

    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
            return data.get("start_offset", 0), data.get("bytes_received", 0)
    except Exception as e:
        logging.error(f"Error reading download status file: {e}")
    return 0, 0

#
# Write the download status file
#
def write_download_status_file(json_file, log_filename, start_offset, bytes_received):
    """Write progress to the JSON file."""
    try:
        with open(json_file, 'w') as file:
            json.dump({
                "log_filename": log_filename,
                "start_offset": start_offset,
                "bytes_received": bytes_received
            }, file)
    except Exception as e:
        logging.error(f"Error writing download status file: {e}")

#
# Download a log file from the flight controller
#
def download_log(connection, log, log_filename):
    """Download a log using MAVLink2."""
    try:

        log_filename_tmp = f"{log_filename}.tmp"
        log_download_status_filename = f"{log_filename}.status.json"

        # Check if MAVLink2 is enabled
        #if not connection.mavlink20():
        #    raise RuntimeError("MAVLink2 is required for faster downloads. Ensure MAVLink2 is enabled.")

        logging.info(f"Downloading log ID {log.id} ({log.size} bytes)...")

        # Initialize start_offset and bytes_received from progress file
        start_offset, bytes_received = read_download_status_file(log_download_status_filename)      

        if start_offset > 0:
            logging.warning(f"Download will resume for {log_filename_tmp} from offset {start_offset}. {bytes_received} bytes were previously downloaded.")

        # Check and trim existing temporary file if necessary
        if Path(log_filename_tmp).exists():
            existing_size = Path(log_filename_tmp).stat().st_size
            if existing_size > bytes_received:
                logging.warning(f"Trimming {log_filename_tmp} from {existing_size} to {bytes_received} bytes.")
                with open(log_filename_tmp, "r+b") as log_file:
                    log_file.truncate(bytes_received)

        chunk_size = 90  # Maximum safe payload size for MAVLink2 LOG_DATA
        
        chunks_downloaded = 0
        num_log_data_timeouts = 0
        
        buffer = bytearray()  # Buffer to accumulate data before writing

        # Request the next chunk of the log
        connection.mav.log_request_data_send(
            target_system=connection.target_system,
            target_component=connection.target_component,
            id=log.id,
            ofs=start_offset,
            count=0xFFFFFFFF
        )

        with open(log_filename_tmp, "ab") as log_file:
            while start_offset < log.size:
                # Check if the drone becomes armed during the download
                if chunks_downloaded % 20000 == 0:
                   if not is_drone_disarmed(connection):
                      raise Exception("Drone became armed. Stopping log download.")

                # Wait for LOG_DATA message
                msg = connection.recv_match(type='LOG_DATA', blocking=True, timeout=0.1)
                if not msg:
                    logging.warning(f"Timeout waiting for log data at offset {start_offset}. Retrying...")
                    num_log_data_timeouts += 1
                    if num_log_data_timeouts > 10:
                        raise Exception(f"Timeout occurred downloading log id {log.id} to file {log_filename}.")
                    continue

                # We received valid log data, reset the timeout counter
                num_log_data_timeouts = 0

                # Calculate the number of valid bytes since the message payload size is fixed at 90 bytes
                valid_bytes = min(log.size - start_offset, len(msg.data))
                
                # Write the received data to the file
                valid_data = bytes(msg.data[:valid_bytes])  # Trim to valid bytes

                # Accumulate valid data in the buffer
                buffer.extend(valid_data)

                start_offset += len(valid_data)
                bytes_received += len(valid_data)
                chunks_downloaded += 1

                # Logging progress and incrementally write to file
                if chunks_downloaded % 10000 == 0 or bytes_received == log.size:
                    percent_complete = (bytes_received / log.size) * 100
                    logging.info(f"Log {log.id}: {bytes_received} / {log.size} bytes ({percent_complete:.2f}% complete)")
                    
                    log_file.write(buffer)
                    buffer.clear()

                    write_download_status_file(log_download_status_filename, log_filename, start_offset, bytes_received)

        # If the log file already exists, then remove it before we rename the temporary file
        # just downloaded to the log filename
        if Path(log_filename).exists():
            Path(log_filename).unlink()

        # Rename the file from the temporary file name
        os.rename(log_filename_tmp, log_filename)

        logging.info(f"Log {log.id} downloaded successfully to {log_filename}.")

        # Remove progress file after successful download
        if Path(log_download_status_filename).exists():
            Path(log_download_status_filename).unlink()

    except Exception as e:
        logging.error(f"Error downloading log {log.id}: {e}", exc_info=True)
        try:
            #if Path(log_filename_tmp).exists():
            #    Path(log_filename_tmp).unlink()            

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
        # Convert the timestamp to a datetime object
        log_date = datetime.datetime.fromtimestamp(msg.time_utc, datetime.timezone.utc)
        # Format the datetime object as a string
        formatted_log_date_string = log_date.strftime("%m/%d/%Y %H:%M:%S")
  
        logging.info(f"Log ID: {msg.id}, Size: {msg.size}, Date: {formatted_log_date_string}, TimeUTC: {msg.time_utc}, NumLogs: {msg.num_logs}, LastLogNum: {msg.last_log_num}")

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

        # If the log never got a valid date/time to it, skip it. 315532800 = 01/01/1980 00:00:00
        #if log.time_utc == 315532800:
        #    logging.info(f"Skipping Log ID {log.id} since its time_utc is invalid (315532800 = 01/01/1980 00:00:00).")
        #    continue

        # Check if the log file already exists
        log_filename = f"{log_output_directory}/log_{log.id:08}.bin"
        if Path(f"{log_filename}").exists():
            # See if the log file is the same size in bytes
            local_log_file_size = os.path.getsize(log_filename)
            if local_log_file_size == log.size:
                logging.info(f"Log ID {log.id} already exists. Skipping download.")
                continue
            else:
                logging.info(f"Log ID {log.id} already exists but file sizes are different. File will be downloaded and the local log file overwritten. Local log file size is {local_log_file_size} bytes, remote log file size is {log.size} bytes.")

        download_log(connection, log, log_filename)


#
# Main program logic
#
def main():
    drone = None

    try:
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