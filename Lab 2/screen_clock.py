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

frames = []
for frame in ImageSequence.Iterator(gif):

    processed_frame = frame.resize((width, height)).convert("RGB")
    frames.append(processed_frame)

num_frames = len(frames)
frame_index = 0


buttonA = digitalio.DigitalInOut(board.D23)    # GPIO23 (PIN 16)
buttonB = digitalio.DigitalInOut(board.D24)    # GPIO24 (PIN 18)
# Use internal pull-ups; buttons then read LOW when pressed.
buttonA.switch_to_input(pull=digitalio.Pull.UP)
buttonB.switch_to_input(pull=digitalio.Pull.UP)
speed = 0.2
cups = 0
textFont = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 25)

while True:

    a_pressed = (buttonA.value == False)
    b_pressed = (buttonB.value == False)

    if a_pressed and b_pressed:
        speed = 0.2
    elif a_pressed:
        if speed > 0.1:
            speed -= 0.05
    elif b_pressed:
        if speed < 1:
            speed += 0.05

    frame_to_display = frames[frame_index].copy()

    draw = ImageDraw.Draw(frame_to_display)

    text = str(cups) + (" cup" if cups == 1 else " cups")
    x = 30
    y = height / 2 - 20
    draw.text((x, y), text, fill=(0, 0, 0), font=textFont)

    disp.image(frame_to_display, rotation)

    frame_index += 1
    if frame_index >= num_frames:
        cups += 1
        frame_index = 0

    time.sleep(speed)
