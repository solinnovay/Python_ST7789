#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

import ST7789 as TFT
import datetime
from time import sleep

from PIL import Image, ImageDraw, ImageFont, ImageColor

import numpy as np

# Raspberry Pi pin configuration:
RST = 27
DC  = 25
LED = 24
SPI_PORT = 0
SPI_DEVICE = 0
SPI_MODE = 0b11
SPI_SPEED_HZ = 40000000

def expand2square(pil_img, background_color):
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result


disp = TFT.ST7789(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=SPI_SPEED_HZ),
       mode=SPI_MODE, rst=RST, dc=DC, led=LED)

# Initialize display.
disp.begin()

# Clear display.
disp.clear()

# Analogue clock setting
width = 240
height = 240
w = width       # screen width
h = height      # screen height
dx = 30         # distance between edge of clock and left edge of screen
dy = 57         # distance between edge of clock and bottom edge of screen
r = 90          # r of clock circle
Ls = r - 2      # length of second hand of watch
Lm = r - 8      # length of minute hand of watch
Lh = Lm - 16    # length of hour hand of watch
X1 = w-1-r*2-dx
Y1 = h-1-r*2-dy
X2 = w-1-dx
Y2 = h-1-dy
Xc = w-1-r-dx   # X coordinates of the center of clock
Yc = h-1-r-dy   # Y coordinates of the conter of clock
Pi = 3.14159265358979  # number pi

image1 = Image.new("RGB", (disp.width, disp.height), "BLACK")
draw = ImageDraw.Draw(image1)

# Initial screen (Demonstration for displaying images)
image2 = Image.open('raspberry_pi_clock.jpg')
image2.thumbnail((240, 240), Image.ANTIALIAS)
image2 = expand2square(image2, (0,0,0))
image3 = Image.open('raspberry_pi_clock.jpg')
image3.thumbnail((120, 120), Image.ANTIALIAS)
image3 = expand2square(image3, (0,0,0))

disp.display(image1)
sleep(0.2)
disp.display(image3,0,0,119,119)
sleep(0.2)
disp.display(image3,120,0,239,119)
sleep(0.2)
disp.display(image3,0,120,119,239)
sleep(0.2)
disp.display(image3,120,120,239,239)
sleep(1)
disp.display(image1)
sleep(0.2)
image4 = Image.open('1.jpg')
image4.thumbnail((240, 240), Image.ANTIALIAS)
image4 = expand2square(image4, (0,0,0))
disp.display(image4)
sleep(0.5)
image5 = Image.open('2.jpg')
image5.thumbnail((240, 240), Image.ANTIALIAS)
image5 = expand2square(image5, (0,0,0))
disp.display(image5)
sleep(0.5)
image6 = Image.open('3.jpg')
image6.thumbnail((240, 240), Image.ANTIALIAS)
image6 = expand2square(image6, (0,0,0))
disp.display(image6)
sleep(0.5)
image7 = Image.open('4.jpg')
image7.thumbnail((240, 240), Image.ANTIALIAS)
image7 = expand2square(image7, (0,0,0))
disp.display(image7)
sleep(0.5)
disp.display(image1)
sleep(0.2)
image4.thumbnail((120, 120), Image.ANTIALIAS)
image4 = expand2square(image4, (0,0,0))
disp.display(image4,0,0,119,119)
sleep(0.2)
image5.thumbnail((120, 120), Image.ANTIALIAS)
image5 = expand2square(image5, (0,0,0))
disp.display(image5,120,0,239,119)
sleep(0.2)
image6.thumbnail((120, 120), Image.ANTIALIAS)
image6 = expand2square(image6, (0,0,0))
disp.display(image6,0,120,119,239)
sleep(0.2)
image7.thumbnail((120, 120), Image.ANTIALIAS)
image7 = expand2square(image7, (0,0,0))
disp.display(image7,120,120,239,239)
sleep(1)
disp.display(image1)
sleep(0.2)
disp.display(image2)
sleep(0.5)

# font setting
font = ImageFont.load_default()
fontJ = ImageFont.truetype('DejaVuSans.ttf', 28, encoding='unic')

Weekday = ("Mon","Tue","Wed","Thu","Fri","Sat","Sun")

def draw_rotated_text(image, text, position, angle, font, fill=(255,255,255)):
    #print position
    position = position[0], position[1]
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0,0,0,0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0,0), text, font=font, fill=fill)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)

try:
    last_time = ""
    time = datetime.datetime.now().time().strftime("%H:%M:%S")
    disp.display(image1)
    while 1:
        #draw = disp.draw()
        # Create blank image for drawing.
        image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
        draw = ImageDraw.Draw(image1)

        while time == last_time:
            sleep(0.1)
            time = datetime.datetime.now().time().strftime("%H:%M:%S")
        last_time = time
        H = int(time[0:2])
        M = int(time[3:5])
        S = int(time[6:8])

        # Analogue clock
        draw.ellipse((X1, Y1, X2, Y2), outline=(255,255,255), fill=(0,0,0))
        draw.line((Xc, Yc, Xc+Ls*np.sin(Pi*(S/30.0)), Yc-Ls*np.cos(Pi*(S/30.0))), fill=(255,0,0))
        draw.line((Xc, Yc, Xc+Lm*np.sin(Pi*((M/30.0 + S/1800.0))), Yc-Lm*np.cos(Pi*((M/30.0 + S/1800.0)))), fill=(255,255,0))
        draw.line((Xc, Yc, Xc+Lh*np.sin(Pi*((H/6.0 + M/360.0 + S/1800.0/12.0))), Yc-Lh*np.cos(Pi*((H/6.0 + M/360.0 + S/1800.0/12.0)))), fill=(63,255,63))

        # Digital clock
        draw.rectangle((0, 184, 239, 239), outline=(0,0,0), fill=(0,0,0))
        now = datetime.datetime.now()
        date = now.date().strftime("%Y/%m/%d")
        weekday = Weekday[now.weekday()]
        time = now.time().strftime("%H:%M:%S")
        draw_rotated_text(image1, date + "(" + weekday + ")", (15,185), 0, font=fontJ, fill=(255,255,0) )
        draw_rotated_text(image1, time, (60,213), 0, font=fontJ, fill=(255,255,0) )
        disp.display(image1)

except KeyboardInterrupt:
    pass
finally:
    disp.clear()
    disp.display(image1)

    image = Image.open('raspberry_pi_clock.jpg')
    image.thumbnail((240, 240), Image.ANTIALIAS)
    image = expand2square(image, (0,0,0))
    disp.display(image2)
    sleep(1)

    disp.clear()
    image1 = Image.new("RGB", (disp.width, disp.height), "BLACK")
    draw = ImageDraw.Draw(image1)
    disp.display(image1)
