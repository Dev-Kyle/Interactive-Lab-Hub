#!/usr/bin/env python3
"""
Distributed Bird Guessing Game Client
Connects to the Socket.IO server and uses an ST7789 display
and buttons for gameplay.
"""

import socketio
import time
import uuid
import signal
import socket
import subprocess

# --- Configuration ---
# !!! IMPORTANT: Change this to your server's IP address !!!
SERVER_URL = "http://10.56.6.10:5001" 

# --- Global State ---
sio = socketio.Client(reconnection_attempts=5, reconnection_delay=1)
MY_GUESS = 0
GAME_STATE = 'IDLE' # 'IDLE', 'GUESSING'
MY_MAC = "00:00:00:00:00:00" # Placeholder, will be set in main()

# --- Display Setup ---
try:
    import board
    import digitalio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_rgb_display.st7789 as st7789
    DISPLAY_AVAILABLE = True
    print("Display libraries loaded.")
except ImportError:
    DISPLAY_AVAILABLE = False
    print("Display libraries not available - running in headless mode")

# Display globals
disp = None
draw = None
image = None
buttonA = None
buttonB = None
font = None

def get_mac_address():
    """Get the MAC address of the primary network interface"""
    try:
        # Try to get MAC from eth0 or wlan0
        result = subprocess.run(['cat', '/sys/class/net/eth0/address'],
                                capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return result.stdout.strip()
        
        result = subprocess.run(['cat', '/sys/class/net/wlan0/address'],
                                capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return result.stdout.strip()
            
    except Exception as e:
        print(f"Error getting hardware MAC address: {e}")
    
    # Fallback to UUID-based MAC
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
    print(f"Using UUID-based MAC: {mac}")
    return mac


def setup_display():
    """Setup the MiniPiTFT display if available"""
    if not DISPLAY_AVAILABLE:
        return None, None, None, None, None, None
    
    try:
        # Configuration for CS and DC pins
        cs_pin = digitalio.DigitalInOut(board.D5)    # GPIO5 (PIN 29)
        dc_pin = digitalio.DigitalInOut(board.D25)   # GPIO25 (PIN 22)
        reset_pin = None

        BAUDRATE = 64000000

        backlight = digitalio.DigitalInOut(board.D22)
        backlight.switch_to_output()
        backlight.value = True
        
        # Buttons with pull-ups (active LOW when pressed)
        btnA = digitalio.DigitalInOut(board.D23)
        btnB = digitalio.DigitalInOut(board.D24)
        btnA.switch_to_input(pull=digitalio.Pull.UP)
        btnB.switch_to_input(pull=digitalio.Pull.UP)

        spi = board.SPI()

        disp_instance = st7789.ST7789(
            spi,
            cs=cs_pin,
            dc=dc_pin,
            rst=reset_pin,
            baudrate=BAUDRATE,
            width=135,
            height=240,
            x_offset=53,
            y_offset=40,
            rotation=90  # Rotate 90 degrees
        )

        # After rotation, width and height are swapped
        width = 240
        height = 135
        img = Image.new("RGB", (width, height))
        draw_instance = ImageDraw.Draw(img)
        
        # Load a font
        try:
            font_instance = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 18)
        except IOError:
            print("Default font not found, using load_default().")
            font_instance = ImageFont.load_default()

        print("[OK] Display initialized (240x135 rotated)")

        return disp_instance, draw_instance, img, btnA, btnB, font_instance
    except Exception as e:
        print(f"Error setting up display: {e}")
        return None, None, None, None, None, None

def update_display(lines):
    """Draws text lines onto the display"""
    if not disp or not draw or not image:
        return # No display available
    
    try:
        # Clear screen to black
        draw.rectangle((0, 0, image.width, image.height), fill=(0, 0, 0))
        
        text_color = (255, 255, 255) # White
        
        y_offset = 5
        for line in lines:
            draw.text((5, y_offset), line, font=font, fill=text_color)
            y_offset += 20 # Spacing
            
        disp.image(image)
    except Exception as e:
        print(f"Error updating display: {e}")

# --- Button Handlers ---
def increment_guess():
    global MY_GUESS
    if GAME_STATE == 'GUESSING':
        MY_GUESS += 1
        print(f"Guess is now: {MY_GUESS}")
        update_display([
            f"GUESSING! (MAC: {MY_MAC[:8]}...)",
            f"Your Guess: {MY_GUESS}"
        ])
    else:
        print("Cannot change guess, not in guessing round.")

def decrement_guess():
    global MY_GUESS
    if GAME_STATE == 'GUESSING':
        MY_GUESS = max(0, MY_GUESS - 1) # Don't go below 0
        print(f"Guess is now: {MY_GUESS}")
        update_display([
            f"GUESSING! (MAC: {MY_MAC[:8]}...)",
            f"Your Guess: {MY_GUESS}"
        ])
    else:
        print("Cannot change guess, not in guessing round.")

# --- SocketIO Event Handlers ---
@sio.on('connect')
def on_connect():
    global MY_MAC
    sio.emit('register', {'mac': MY_MAC})
    print(f"Sent registration as '{MY_MAC}'")
    update_display([
        f"Connected!",
        f"MAC: {MY_MAC}",
        "Waiting for game..."
    ])

@sio.on('disconnect')
def on_disconnect():
    print("\n! Disconnected from server. Will try to reconnect...")
    update_display(["Disconnected.", "Retrying..."])

@sio.on('new_round')
def on_new_round(data):
    """Server has started a new round"""
    global MY_GUESS, GAME_STATE
    MY_GUESS = 0 # Reset guess
    GAME_STATE = 'GUESSING'
    print("\n" + "="*30)
    print(f"  NEW ROUND! Start Guessing!")
    print(f"  You have {data.get('countdown', 10)} seconds.")
    print(f"  My guess is reset to: {MY_GUESS}")
    print("="*30)
    update_display([
        f"NEW ROUND! {data.get('countdown')}s",
        f"Your Guess: {MY_GUESS}"
    ])
    
@sio.on('times_up')
def on_times_up():
    """Server says time is up, submit the guess"""
    global GAME_STATE
    if GAME_STATE == 'GUESSING':
        GAME_STATE = 'IDLE' # Stop accepting button presses
        print("\n! Time's Up!")
        print(f"  Submitting final guess: {MY_GUESS}")
        try:
            sio.emit('submit_guess', {'mac': MY_MAC, 'guess': MY_GUESS})
            print("  Guess submitted successfully.")
            update_display([
                f"Time's Up!",
                f"Submitted: {MY_GUESS}",
                "Waiting for results..."
            ])
        except Exception as e:
            print(f"  Error submitting guess: {e}")
    
@sio.on('round_idle')
def on_round_idle():
    """Server is back in the 'waiting' state"""
    global GAME_STATE
    GAME_STATE = 'IDLE'
    print("\n--- Round over. Waiting for next game... ---")
    update_display([
        f"Round Over.",
        f"MAC: {MY_MAC}",
        "Waiting for game..."
    ])

# --- Main Execution ---
def main():
    global MY_MAC, disp, draw, image, buttonA, buttonB, font
    
    print("=" * 40)
    print(" Bird Guessing Game Client (Display Ver.)")
    
    MY_MAC = get_mac_address()
    print(f" Client MAC: {MY_MAC}")
    print(f" Server URL: {SERVER_URL}")
    print("=" * 40)
    
    # Setup display
    disp, draw, image, buttonA, buttonB, font = setup_display()
    
    # Graceful exit handler
    def signal_handler(signum, frame):
        print("\nShutting down gracefully...")
        if sio.connected:
            sio.disconnect()
        if DISPLAY_AVAILABLE and backlight:
            backlight.value = False # Turn off backlight
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)

    # Main connection loop
    while True:
        try:
            print(f"Attempting to connect to {SERVER_URL}...")
            update_display(["Connecting to server..."])
            sio.connect(SERVER_URL)
            
            print("Connection established. Starting button poll loop...")
            
            # --- Button Polling Loop ---
            # This loop runs while sio is connected.
            # The sio events run on a background thread.
            while sio.connected:
                if buttonA and (not buttonA.value): # Button A pressed (logic is pulled up)
                    increment_guess()
                    time.sleep(0.15) # Debounce
                    
                if buttonB and (not buttonB.value): # Button B pressed
                    decrement_guess()
                    time.sleep(0.15) # Debounce
                    
                time.sleep(0.01) # Prevent CPU spinning
            
            # If we exit the inner loop, it means we disconnected
            print("Lost connection.")
            update_display(["Connection lost.", "Retrying..."])
            time.sleep(3)

        except socketio.exceptions.ConnectionError as e:
            print(f"Connection failed: {e}")
            print("Retrying in 5 seconds...")
            update_display(["Connection failed.", "Retrying in 5s..."])
            time.sleep(5)
        except KeyboardInterrupt:
            print("\nCaught interrupt, shutting down.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            print("Retrying in 10 seconds...")
            time.sleep(10)
            
    if sio.connected:
        sio.disconnect()
    print("Client shut down.")

if __name__ == '__main__':
    main()
