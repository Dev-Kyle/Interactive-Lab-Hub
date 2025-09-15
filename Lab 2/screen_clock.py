import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import adafruit_rgb_display.st7789 as st7789

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.D5)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

gif = Image.open('drip.gif')

# Create a list to hold the processed frames
frames = []
# Loop through each frame of the GIF
for frame in ImageSequence.Iterator(gif):
    # Convert the frame to the '1' format (1-bit black and white)
    # This is necessary for monochrome OLED displays
    processed_frame = frame.convert('1')

    # Resize the frame to fit the display
    processed_frame = processed_frame.resize((width, height))

    frames.append(processed_frame)

# Get the number of frames to loop through
num_frames = len(frames)
frame_index = 0

## --- Step 2: Modify Your Main Loop to Animate ---
print("Playing animation...")
while True:
    # Get the current frame from your list
    current_frame = frames[frame_index]

    # Display the frame on the screen
    disp.image(current_frame)
    disp.display()

    # Move to the next frame
    frame_index += 1
    # If we've reached the end of the GIF, loop back to the beginning
    if frame_index >= num_frames:
        frame_index = 0

    # Control the animation speed (e.g., 0.1 seconds per frame)
    time.sleep(0.1)
