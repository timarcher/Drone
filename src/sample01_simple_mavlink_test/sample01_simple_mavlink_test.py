# This script shows the basics of how to communicate with the ArduPilot flight controller.
# It prints out info from the flight controller. It assumes you have a HereLink Air Unit 
# at IP 192.168.144.10 and the Raspberry Pi can connect to it.
# It simply calls the read_telemetry function to print out several stats from the flight controller.

import time
import signal
import traceback
from pymavlink import mavutil

#
# Connect to drone
#
def connect(connection_string):
    drone = mavutil.mavlink_connection(connection_string)

    # This workaround seems to be needed otherwise connections to the Herelink fail
    # waiting for the heartbeat
    drone.mav.ping_send(
        int(time.time() * 1e6), # Unix time in microseconds
        0, # Ping number
        0, # Request ping of all systems
        0 # Request ping of all components
    )

    drone.wait_heartbeat()
    print(f"Heartbeat from system (system {drone.target_system} component {drone.target_component})")

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
            print(f"Pitch: {msg.pitch}, Roll: {msg.roll}, Yaw: {msg.yaw}")
        elif msg.get_type() == 'GLOBAL_POSITION_INT':
            print(f"Lat: {msg.lat}, Lon: {msg.lon}, Alt: {msg.alt}")
        elif msg.get_type() == 'BATTERY_STATUS':
            voltage = msg.voltages[0] / 1000.0  # Voltage in volts
            remaining = msg.battery_remaining  # Remaining battery in percentage
            print(f"Battery Voltage: {voltage:.2f}V, Remaining: {remaining}%")
        elif msg.get_type() == 'HEARTBEAT':
            # Extract flight mode
            mode = drone.flightmode
            # Extract arming status
            armed = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
            print(f"Flight Mode: {mode}, Armed: {armed}")

        # Sleep to prevent flooding the console
        time.sleep(0.05)

#
# Helper function to close the connection to the drone
#
def close_connection(drone):
    print("Closing connection to the drone...")
    drone.close()
    print("Connection closed.")

#
# Signal handler function
#
def signal_handler(sig, frame, drone):
    print(f"Received signal {sig}.")
    close_connection(drone)
    print("Graceful shutdown completed.")
    exit(0)

#
# Main program logic
#
def main():
    connection_string = "udpout:192.168.144.10:14552"
    drone = connect(connection_string);

    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, drone))
    signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame, drone))

    try:
      # Set message rates (example: 10 Hz for attitude and global position)
      set_message_rate(drone, mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 10)
      set_message_rate(drone, mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 10)
      set_message_rate(drone, mavutil.mavlink.MAVLINK_MSG_ID_BATTERY_STATUS, 1)
      set_message_rate(drone, mavutil.mavlink.MAVLINK_MSG_ID_HEARTBEAT, 1)

      # Start reading telemetry data
      read_telemetry(drone)

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
    finally:
        close_connection(drone)

if __name__ == "__main__":
    main()