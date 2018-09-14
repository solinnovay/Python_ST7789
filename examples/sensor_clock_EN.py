#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

import ST7789 as TFT
import datetime
from time import sleep

from PIL import Image, ImageDraw, ImageFont, ImageColor

import numpy as np

from Adafruit_BME280 import *

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
dx = 40         # distance between edge of clock and left edge of screen
dy = 77         # distance between edge of clock and bottom edge of screen
r = 80          # r of clock circle
Ls = r - 2      # length of second hand of watch
Lm = r - 8      # length of minute hand of watch
Lh = Lm - 16    # length of hour hand of watch
X1 = w-1-r*2-dx #
Y1 = h-1-r*2-dy #
X2 = w-1-dx     #
Y2 = h-1-dy     #
Xc = w-1-r-dx   # X coordinates of the center of clock
Yc = h-1-r-dy   # Y coordinates of the conter of clock
Pi = 3.14159265358979  # number pi

image1 = Image.new("RGB", (disp.width, disp.height), "BLACK")
draw = ImageDraw.Draw(image1)

# Initial screen (Demonstration for displaying images)
image = Image.open('raspberry_pi_clock.jpg')
image.thumbnail((240, 240), Image.ANTIALIAS)
image = expand2square(image, (0,0,0))

disp.display(image)
sleep(1)

# font setting
font = ImageFont.load_default()
fontJ = ImageFont.truetype('DejaVuSans.ttf', 24, encoding='unic')
fontS = ImageFont.truetype('DejaVuSans.ttf', 18, encoding='unic')

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
    sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
    degrees = sensor.read_temperature()
    pascals = sensor.read_pressure()
    hectopascals = pascals / 100
    humidity = sensor.read_humidity()

    last_time = ""
    time = datetime.datetime.now().time().strftime("%H:%M:%S")
    disp.display(image1)
    while 1:

        if time[6:8] == "00":
            sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
            degrees = sensor.read_temperature()
            pascals = sensor.read_pressure()
            hectopascals = pascals / 100
            humidity = sensor.read_humidity()

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
        draw.rectangle((0, 164, 239, 239), outline=(0,0,0), fill=(0,0,0))
        now = datetime.datetime.now()
        date = now.date().strftime("%m/%d")
        weekday = Weekday[now.weekday()]
        time = now.time().strftime("%H:%M:%S")
        draw_rotated_text(image1, date + "(" + weekday + ")" + time, (1,163), 0, font=fontJ, fill=(255,255,0) )

        # Sensor measured result
        text1 = "Temp:{0:0.1f}'C".format(degrees)
        text2 = "Humid:{0:0.0f}%".format(humidity)
        text3 = "Press:{0:0.2f}hPa".format(hectopascals)
        draw_rotated_text(image1, text1 + " " + text2, (0,190), 0, font=fontS, fill=(255,255,0) )
        draw_rotated_text(image1, text3, (35,216), 0, font=fontS, fill=(255,255,0) )

        disp.display(image1)


except KeyboardInterrupt:
    pass
finally:
    disp.clear()
    disp.display(image)

    image = Image.open('raspberry_pi_clock.jpg')
    image.thumbnail((240, 240), Image.ANTIALIAS)
    image = expand2square(image, (0,0,0))
    disp.display(image)
    sleep(1)

    disp.clear()
    image1 = Image.new("RGB", (disp.width, disp.height), "BLACK")
    draw = ImageDraw.Draw(image1)
    disp.display(image1)
