# Create a Cylon-like scanning effect where the LEDs start at each end of the strip, 
# move toward the center, and then reverse direction back to each end.

from pi5neo import Pi5Neo
import time

# User-Configurable Variables
NUM_LEDS = 89                           # Total number of LEDs (I have 97 LEDs, but I use 90 to make it look centered, the last 6 in back dont get lit up)
SPI_DEVICE = '/dev/spidev0.0'           # SPI device
SPI_SPEED = 800                         # SPI speed in kHz
DELAY = 0.01                            # Delay between updates (speed of movement)
STRIP_COLOR = (50, 0, 0)                # Color and brightness of the whole strip (R, G, B)
SCANNING_LEDS = 3                       # Number of LEDs in the scanning section
SCANNING_GRADIENT = [180, 255, 180]     # Gradient for scanning LEDs (brightness levels)
SCANNING_COLOR = (0, 0, 255)            # Scanning color set to blue (R, G, B)

# Initialize the Pi5Neo class
neo = Pi5Neo(SPI_DEVICE, NUM_LEDS, SPI_SPEED)

def initialize_strip(neo):
    """
    Initializes the entire LED strip with the base strip color.

    Args:
        neo: The initialized Pi5Neo object.
    """
    neo.fill_strip(*STRIP_COLOR)
    neo.update_strip()  # Commit changes to the LEDs

def dual_end_cylon_scan(neo):
    """
    Creates a dual-end Cylon scanning effect on the LED strip.

    Args:
        neo: The initialized Pi5Neo object.
    """
    previous_positions = []  # Track the last updated positions

    while True:
        # Scanning from ends to the center
        for i in range(NUM_LEDS // 2 + 1):
            left_position = i
            right_position = NUM_LEDS - 1 - i
            previous_positions = update_strip_with_dual_scanning_pattern(neo, left_position, right_position, previous_positions)
            time.sleep(DELAY)

        # Scanning from the center back to the ends
        for i in range(NUM_LEDS // 2, -1, -1):
            left_position = i
            right_position = NUM_LEDS - 1 - i
            previous_positions = update_strip_with_dual_scanning_pattern(neo, left_position, right_position, previous_positions)
            time.sleep(DELAY)

def update_strip_with_dual_scanning_pattern(neo, left_position, right_position, previous_positions):
    """
    Updates only the LEDs that have changed color for the dual-end scanning effect.

    Args:
        neo: The initialized Pi5Neo object.
        left_position: Current position of the scanning section on the left end.
        right_position: Current position of the scanning section on the right end.
        previous_positions: List of previously updated positions.
    
    Returns:
        List of currently updated positions for the scanning LEDs.
    """
    # Calculate the current positions for the scanning gradient
    current_positions = []

    # Left scanning section
    for offset, brightness in enumerate(SCANNING_GRADIENT):
        pos = left_position - offset + SCANNING_LEDS // 2
        if 0 <= pos < NUM_LEDS:
            r = (SCANNING_COLOR[0] * brightness) // 255
            g = (SCANNING_COLOR[1] * brightness) // 255
            b = (SCANNING_COLOR[2] * brightness) // 255
            neo.set_led_color(pos, r, g, b)
            current_positions.append(pos)

    # Right scanning section
    for offset, brightness in enumerate(SCANNING_GRADIENT):
        pos = right_position - offset + SCANNING_LEDS // 2
        if 0 <= pos < NUM_LEDS:
            r = (SCANNING_COLOR[0] * brightness) // 255
            g = (SCANNING_COLOR[1] * brightness) // 255
            b = (SCANNING_COLOR[2] * brightness) // 255
            neo.set_led_color(pos, r, g, b)
            current_positions.append(pos)

    # Restore base color for previous positions not in current positions
    for prev_pos in previous_positions:
        if prev_pos not in current_positions:
            neo.set_led_color(prev_pos, *STRIP_COLOR)

    # Commit changes to the strip
    neo.update_strip()

    return current_positions

# Main function
if __name__ == "__main__":
    try:
        print("Initializing LED strip...")
        initialize_strip(neo)  # Fill strip with base color
        print("Starting dual-end Cylon scanning pattern. Press Ctrl+C to stop.")
        dual_end_cylon_scan(neo)
    except KeyboardInterrupt:
        print("Exiting...")
        neo.fill_strip(0, 0, 0)  # Turn off all LEDs
        neo.update_strip()
