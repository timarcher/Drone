from pi5neo import Pi5Neo
import time

NUM_LEDS = 97                           # Total number of LEDs

def loading_bar(neo):
    for i in range(neo.num_leds):
        neo.set_led_color(i, 0, 255, 0)  # Green loading bar
        neo.update_strip()
        time.sleep(0.2)
    neo.clear_strip()
    neo.update_strip()

neo = Pi5Neo('/dev/spidev0.0', NUM_LEDS, 800)
loading_bar(neo)
