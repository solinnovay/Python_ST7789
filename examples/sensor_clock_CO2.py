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
import os

CO2_file = "/var/run/CO2.txt"

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

# アナログ時計描画用常数設定
width = 240
height = 240
w = width  # 画面幅
h = height # 画面高
dx = 40         # 時計の円とキャンバスの左側の枠線との間隔
dy = 77         # 時計の円とキャンバスの下側の枠線との間隔
r = 80          # 時計の円の半径
Ls = r - 2      # 秒針の長さ
Lm = r - 8      # 長針の長さ
Lh = Lm - 16    # 短針の長さ
X1 = w-1-r*2-dx # 時計の枠の円の外接正方形の左上頂点のX座標
Y1 = h-1-r*2-dy # 時計の枠の円の外接正方形の左上頂点のY座標
X2 = w-1-dx     # 時計の枠の円の外接正方形の右下頂点のX座標
Y2 = h-1-dy     # 時計の枠の円の外接正方形の右下頂点のY座標
Xc = w-1-r-dx   # 時計の枠の円の中心のX座標
Yc = h-1-r-dy   # 時計の枠の円の中心のY座標
Pi = 3.14159265358979  # 円周率

image1 = Image.new("RGB", (disp.width, disp.height), "BLACK")
draw = ImageDraw.Draw(image1)

# 初期画面：ラズパイのロゴを表示
image = Image.open('raspberry_pi_clock.jpg')
image.thumbnail((240, 240), Image.ANTIALIAS)
image = expand2square(image, (0,0,0))
#image = image.rotate(90) # 横向きにする場合は、この行を有効化
disp.display(image)
sleep(1)

# 図形描画
# ellipse：円・楕円の描画
# rectangle：長方形の描画
# polygon：三角形の描画
# line：直線（線分）の描画
#
#【引数】
#　第１引数：頂点座標
#　　　　　　　円・楕円：外接長方形の(左上頂点X,Y, 右下頂点X,Y)
#　　　　　　　長方形：　長方形の(左上頂点X,Y, 右下頂点X,Y)
#　　　　　　　三角形：　三角形の[(頂点1 X,Y), (頂点2 X,Y), (頂点3 X,Y)]
#　　　　　　　直線：　　三角形の(頂点1 X,Y, 頂点2 X,Y, 頂点3 X,Y)
#　outline：枠線の色指定 (R,G,B)
#　fill： 　塗り色指定 (R,G,B)
#【記述例】
#  draw.ellipse((10,10, 50,50), outline=(0,255,0), fill=(0,0,255))
#  draw.rectangle((60,10, 100,50), outline=(255,255,0), fill=(255,0,255))
#  draw.polygon([(80,10), (110,50), (70,50)], outline=(0,0,0), fill=(0,255,255))
#  draw.line((10,170, 110,230), fill=(255,255,255))
#  draw.line((10,230, 110,170), fill=(255,255,255))

# フォントの読み込み
font = ImageFont.load_default()
fontJ = ImageFont.truetype('/usr/share/fonts/truetype/kochi/kochi-gothic-subst.ttf', 28, encoding='unic')
fontS = ImageFont.truetype('/usr/share/fonts/truetype/kochi/kochi-gothic-subst.ttf', 25, encoding='unic')
#fontSS = ImageFont.truetype('/usr/share/fonts/truetype/kochi/kochi-gothic.ttf', 21, encoding='unic')
fontSS = ImageFont.truetype('ipag.ttf', 21, encoding='unic')

# 曜日番号→日本語曜日変換定義
Weekday = (u"月",u"火",u"水",u"木",u"金",u"土",u"日")

# この液晶モニタは、横置きをベースにアドレスが定義されているため、縦横変換処理を定義
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

    if os.path.exists(CO2_file):
        f = open(CO2_file, "r")
        co2 = f.read()
        f.close()
    else:
        co2 = ""

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
            if os.path.exists(CO2_file):
                f = open(CO2_file, "r")
                co2 = f.read()
                f.close()
            else:
                co2 = ""

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

        # アナログ時計
        draw.ellipse((X1, Y1, X2, Y2), outline=(255,255,255), fill=(0,0,0))  # 時計の描画
        #draw.line((Xc, Yc, Xc+Ls*np.sin(Pi*(S/30.0-0.5)), Yc-Ls*np.cos(Pi*(S/30.0-0.5))), fill=(255,0,0))        # 秒針の描画
        #draw.line((Xc, Yc, Xc+Lm*np.sin(Pi*((M/30.0 + S/1800.0)-0.5)), Yc-Lm*np.cos(Pi*((M/30.0 + S/1800.0)-0.5))), fill=(255,255,0))        # 長針の描画
        #draw.line((Xc, Yc, Xc+Lh*np.sin(Pi*((H/6.0 + M/360.0 + S/1800.0/12.0)-0.5)), Yc-Lh*np.cos(Pi*((H/6.0 + M/360.0 + S/1800.0/12.0)-0.5))), fill=(63,255,63))  # 短針の描画
        draw.line((Xc, Yc, Xc+Ls*np.sin(Pi*(S/30.0)), Yc-Ls*np.cos(Pi*(S/30.0))), fill=(255,0,0))        # 秒針の描画
        draw.line((Xc, Yc, Xc+Lm*np.sin(Pi*((M/30.0 + S/1800.0))), Yc-Lm*np.cos(Pi*((M/30.0 + S/1800.0)))), fill=(255,255,0))        # 長針の描画
        draw.line((Xc, Yc, Xc+Lh*np.sin(Pi*((H/6.0 + M/360.0 + S/1800.0/12.0))), Yc-Lh*np.cos(Pi*((H/6.0 + M/360.0 + S/1800.0/12.0)))), fill=(63,255,63))  # 短針の描画

        # デジタル時計
        draw.rectangle((0, 164, 239, 239), outline=(0,0,0), fill=(0,0,0))
        now = datetime.datetime.now()
        date = now.date().strftime("%m/%d")
        weekday = Weekday[now.weekday()]
        time = now.time().strftime("%H:%M:%S")
        draw_rotated_text(image1, date + "(" + weekday + ")" + time, (1,163), 0, font=fontJ, fill=(255,255,0) )

        # センサー測定値
        text1 = u"気温{0:0.1f}℃".format(degrees)
        text2 = u"湿度{0:0.0f}%".format(humidity)
        text3 = u"気圧{0:0.2f}hPa".format(hectopascals)
        text4 = "CO2:" + co2
        draw_rotated_text(image1, text1 + " " + text4, (0,192), 0, font=fontSS, fill=(255,255,0) )
        draw_rotated_text(image1, text2 + " " + text3, (0,216), 0, font=fontSS, fill=(255,255,0) )

        disp.display(image1)


except KeyboardInterrupt:
    pass
finally:
    disp.clear()
    disp.display(image)

    # ラズパイのロゴを表示
    image = Image.open('raspberry_pi_clock.jpg')
    image.thumbnail((240, 240), Image.ANTIALIAS)
    image = expand2square(image, (0,0,0))
    disp.display(image)
    sleep(1)

    # 画面を消去
    disp.clear()
    image1 = Image.new("RGB", (disp.width, disp.height), "BLACK")
    draw = ImageDraw.Draw(image1)
    disp.display(image1)
