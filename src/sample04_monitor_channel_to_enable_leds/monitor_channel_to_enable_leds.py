# This script will monitor the channel specified below (default is 6)
# If it goes high, it will enable the LED pattern. If it goes low, it will disable the LED pattern.
# It assumes you have a HereLink Air Unit at IP 192.168.144.10 and the Raspberry Pi can connect to it.

import sys
import time
import signal
from threading import Thread, Event
import logging
from logging.handlers import RotatingFileHandler
from pymavlink import mavutil
from pi5neo import Pi5Neo

# Parameters for the script
#connection_string = "udpout:192.168.144.10:14552"  # MAVLink connection string to the HereLink
#baud_rate = 0

connection_string = "udp:127.0.0.1:14551"           # MAVLink connection string to the local MavProxy
baud_rate = 0

#connection_string = "/dev/ttyAMA0"                 # MAVLink connection string to the serial/UART connection
#baud_rate = 921600

channel_to_monitor = 6  # Channel number to monitor (e.g., 6)
threshold_value = 1500  # Threshold for "high" signal

# LED Strip Parameters
NUM_LEDS = 89
SPI_DEVICE = '/dev/spidev0.0'
SPI_SPEED = 800
DELAY = 0.01
STRIP_COLOR = (50, 0, 0)
SCANNING_LEDS = 3
SCANNING_GRADIENT = [180, 255, 180]
SCANNING_COLOR = (0, 0, 255)


# Configure logging to log to both file and system journal (stdout)
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for verbose output
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Logs to systemd journal (stdout)
        RotatingFileHandler(
            "monitor_channel_to_enable_leds.log",  # Log file name
            maxBytes=50 * 1024 * 1024,  # Max size per file: 50 MB
            backupCount=5  # Keep up to 5 backup files
        )        
    ]
)

#
# initialize_strip
#
def initialize_strip(neo):
    """
    Initializes the entire LED strip with the base strip color.
    """
    neo.fill_strip(*STRIP_COLOR)
    neo.update_strip()

#
# clear_strip
#
def clear_strip(neo):
    neo.fill_strip(0, 0, 0)
    neo.update_strip()

#
# dual_end_cylon_scan
#
def dual_end_cylon_scan(neo, stop_event):
    """
    Creates a dual-end Cylon scanning effect on the LED strip in a loop.
    Stops when `stop_event` is set.
    """
    previous_positions = []

    while not stop_event.is_set():
        for i in range(NUM_LEDS // 2 + 1):
            if stop_event.is_set():
                break
            left_position = i
            right_position = NUM_LEDS - 1 - i
            previous_positions = update_strip_with_dual_scanning_pattern(neo, left_position, right_position, previous_positions)
            time.sleep(DELAY)

        for i in range(NUM_LEDS // 2, -1, -1):
            if stop_event.is_set():
                break
            left_position = i
            right_position = NUM_LEDS - 1 - i
            previous_positions = update_strip_with_dual_scanning_pattern(neo, left_position, right_position, previous_positions)
            time.sleep(DELAY)


#
# update_strip_with_dual_scanning_pattern
#
def update_strip_with_dual_scanning_pattern(neo, left_position, right_position, previous_positions):
    """
    Updates only the LEDs that have changed color for the dual-end scanning effect.
    """
    current_positions = []

    for offset, brightness in enumerate(SCANNING_GRADIENT):
        pos = left_position - offset + SCANNING_LEDS // 2
        if 0 <= pos < NUM_LEDS:
            r = (SCANNING_COLOR[0] * brightness) // 255
            g = (SCANNING_COLOR[1] * brightness) // 255
            b = (SCANNING_COLOR[2] * brightness) // 255
            neo.set_led_color(pos, r, g, b)
            current_positions.append(pos)

    for offset, brightness in enumerate(SCANNING_GRADIENT):
        pos = right_position - offset + SCANNING_LEDS // 2
        if 0 <= pos < NUM_LEDS:
            r = (SCANNING_COLOR[0] * brightness) // 255
            g = (SCANNING_COLOR[1] * brightness) // 255
            b = (SCANNING_COLOR[2] * brightness) // 255
            neo.set_led_color(pos, r, g, b)
            current_positions.append(pos)

    for prev_pos in previous_positions:
        if prev_pos not in current_positions:
            neo.set_led_color(prev_pos, *STRIP_COLOR)

    neo.update_strip()
    return current_positions

#
# Connect to drone
#
def connect(connection_string):
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
# Determine if the rc receiver is healthy
#
def is_rc_receiver_healthy(connection, do_retries = False):
    """Check if the rc receiver is health."""
    max_retries = 5
    retries = 0
    while retries < max_retries:
        # Read the next SYS_STATUS message to determine if the RC receiver is found
        msg = connection.recv_match(type='SYS_STATUS', blocking=True, timeout=2)
        if msg:
            # Check RC receiver status
            sensors_present = msg.onboard_control_sensors_present
            sensors_enabled = msg.onboard_control_sensors_enabled
            sensor_health = msg.onboard_control_sensors_health

            #logging.info(f"sensors_present {sensors_present}, sensors_enabled {sensors_enabled}, sensor_health {sensor_health}.")

            # Ignore bad sensor health readings
            if sensors_present == 1 and sensors_enabled == 1 and sensor_health == 0:
                pass
            # RC Receiver might be missing                       
            elif not (sensor_health & mavutil.mavlink.MAV_SYS_STATUS_SENSOR_RC_RECEIVER):
                return False
            else:
                return True

        if not do_retries:
            break

        retries += 1
        #logging.info(f"Checking if the rc receiver is healthy. Attempt {retries} timed out. No valid SYS_STATUS received. Retrying...")
        time.sleep(1)  # Sleep for half second before retrying

    #logging.info(f"Timeout occurred checking if the rc receiver is healthy. Assuming unhealthy.")
    return None


#
# Monitor the channel and enable LEDs
#
def monitor_channel(connection, channel, threshold, neo):
    """
    Monitor a specific RC channel to control LED strip effects.
    """
    scanning_thread = None
    stop_event = Event()
    strip_active = False

    logging.info(f"Setting up monitor on channel {channel}.")

    rc_receiver_healthy = is_rc_receiver_healthy(connection, True)
    last_rc_receiver_health_check_time = time.time() * 1000  # Current time in milliseconds

    try:
        while True:
            should_strip_be_active=False

            # Get the current time in milliseconds
            current_time = time.time() * 1000

            # Only check the rc receiver health every 2 seconds
            if current_time - last_rc_receiver_health_check_time >= 2000:            
                # Read the next SYS_STATUS message to determine if the RC receiver is found
                tmp_health_value = is_rc_receiver_healthy(connection, True)
                if tmp_health_value is not None:
                    rc_receiver_healthy = tmp_health_value
                    last_rc_receiver_health_check_time = current_time


            if not rc_receiver_healthy:
                #logging.warning("RC Receiver not healthy!")
                should_strip_be_active = False
            else:        
                # Get the value of the RC Channel that turns the LED Strip on or off
                msg = connection.recv_match(type="RC_CHANNELS", blocking=True, timeout=5)
                if msg:
                    channel_value = getattr(msg, f"chan{channel}_raw", None)
                    #logging.info(f"Channel Value {channel_value}.")
                    if channel_value is not None:
                        if channel_value > threshold:
                            should_strip_be_active=True
                            if not strip_active:
                                logging.info(f"Channel {channel} HIGH! Activating LED effect.")
                                initialize_strip(neo)
                                stop_event.clear()
                                scanning_thread = Thread(target=dual_end_cylon_scan, args=(neo, stop_event))
                                scanning_thread.start()
                                strip_active = True
                        else:
                            if strip_active:
                                logging.info(f"Channel {channel} LOW. LED strip will be deactivated.")
                            should_strip_be_active=False
                    else:
                        logging.info(f"channel_value is None. Assuming strip should be inactive.")
                        should_strip_be_active=False
                else:
                    logging.info(f"No RC_CHANNELS message received. Assuming strip should be inactive.")
                    should_strip_be_active=False


            if not should_strip_be_active and strip_active:
                logging.info(f"Strip should not be active. Clearing LED strip.")
                stop_event.set()
                if scanning_thread:
                    scanning_thread.join()
                neo.fill_strip(0, 0, 0)
                neo.update_strip()
                strip_active = False
                
    except Exception as e:
        logging.error(f"Error monitoring channel {channel}: {e}", exc_info=True)
        raise


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
# Main program logic
#
def main():
    drone = None
    try:
        logging.info(f"Script starting.")

        # Initialize the Pi5Neo class
        logging.info(f"Initializing NeoPixel interface.")
        neo = Pi5Neo(SPI_DEVICE, NUM_LEDS, SPI_SPEED)

        drone = connect(connection_string)
        logging.info(f"Mavlink connection established to drone.")

        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, drone))
        signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame, drone))

        # Set the rate for RC_CHANNELS to 5 Hz
        #logging.info(f"Setting message rate: {mavutil.mavlink.MAVLINK_MSG_ID_SYS_STATUS}")
        #set_message_rate(drone, mavutil.mavlink.MAVLINK_MSG_ID_SYS_STATUS, 2)

        monitor_channel(drone, channel_to_monitor, threshold_value, neo)
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