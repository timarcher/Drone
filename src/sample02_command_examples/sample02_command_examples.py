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
# Helper function to arm the drone
#
def arm_drone(drone):
    send_command_long(drone, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 1)
    ack = drone.recv_match(type='COMMAND_ACK', blocking=True)
    if ack.command == mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        print("Drone armed successfully")
    else:
        print(f"Failed to arm drone: {ack.result}")
        if ack.result == mavutil.mavlink.MAV_RESULT_TEMPORARILY_REJECTED:
            print("Arming temporarily rejected.")
        elif ack.result == mavutil.mavlink.MAV_RESULT_DENIED:
            print("Arming denied.")
        elif ack.result == mavutil.mavlink.MAV_RESULT_UNSUPPORTED:
            print("Arming command unsupported.")
        elif ack.result == mavutil.mavlink.MAV_RESULT_FAILED:
            print("Arming failed.")
        return False
    return True

#
# Helper function to set the flight mode
#
def set_flight_mode(drone, mode):
    if mode not in drone.mode_mapping():
        print(f"Unknown mode: {mode}")
        return False
    mode_id = drone.mode_mapping()[mode]
    drone.set_mode(mode_id)
    ack = drone.recv_match(type='COMMAND_ACK', blocking=True)
    if ack.command == mavutil.mavlink.MAV_CMD_DO_SET_MODE and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        print(f"Flight mode set to {mode}")
    else:
        print(f"Failed to set flight mode: {ack.result}")
        if ack.result == mavutil.mavlink.MAV_RESULT_TEMPORARILY_REJECTED:
            print("Flight mode change temporarily rejected.")
        elif ack.result == mavutil.mavlink.MAV_RESULT_DENIED:
            print("Flight mode change denied.")
        elif ack.result == mavutil.mavlink.MAV_RESULT_UNSUPPORTED:
            print("Flight mode change unsupported.")
        elif ack.result == mavutil.mavlink.MAV_RESULT_FAILED:
            print("Flight mode change failed.")
        return False
    return True

#
# Helper function to send the takeoff command to a specific altitude
#
def send_takeoff_command(drone, target_altitude):
    send_command_long(drone, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, target_altitude)
    ack = drone.recv_match(type='COMMAND_ACK', blocking=True)
    if ack.command == mavutil.mavlink.MAV_CMD_NAV_TAKEOFF and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        print("Takeoff command accepted")
    else:
        print(f"Failed to take off: {ack.result}")
        if ack.result == mavutil.mavlink.MAV_RESULT_TEMPORARILY_REJECTED:
            print("Takeoff temporarily rejected.")
        elif ack.result == mavutil.mavlink.MAV_RESULT_DENIED:
            print("Takeoff denied. Check GPS fix and battery levels.")
        elif ack.result == mavutil.mavlink.MAV_RESULT_UNSUPPORTED:
            print("Takeoff command unsupported.")
        elif ack.result == mavutil.mavlink.MAV_RESULT_FAILED:
            print("Takeoff failed.")
        return False
    return True


#
# Helper function to send the land command
#
def send_land_command(drone):
    send_command_long(drone, mavutil.mavlink.MAV_CMD_NAV_LAND)
    ack = drone.recv_match(type='COMMAND_ACK', blocking=True)
    if ack.command == mavutil.mavlink.MAV_CMD_NAV_LAND and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
        print("Land command accepted")
    else:
        print(f"Failed to land: {ack.result}")
        if ack.result == mavutil.mavlink.MAV_RESULT_TEMPORARILY_REJECTED:
            print("Landing temporarily rejected.")
        elif ack.result == mavutil.mavlink.MAV_RESULT_DENIED:
            print("Landing denied.")
        elif ack.result == mavutil.mavlink.MAV_RESULT_UNSUPPORTED:
            print("Landing command unsupported.")
        elif ack.result == mavutil.mavlink.MAV_RESULT_FAILED:
            print("Landing failed.")
        return False
    return True


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

      print(drone.mode_mapping())

      # Set flight mode - STABILIZE, LOITER 
      if not set_flight_mode(drone, "STABILIZE"):
          return

      # Arm the drone
      if not arm_drone(drone):
          return

      # Send a takeoff command to 10 meters altitude
      if not send_takeoff_command(drone, 5):
          return

      # Start reading telemetry data
      read_telemetry(drone)

      # Land drone
      send_land_command(drone)
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
    finally:
        close_connection(drone)

if __name__ == "__main__":
    main()