import network 
import urequests
import utime
import ujson
from machine import Pin, I2C, UART
import ssd1306
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
from dht import DHT11, InvalidChecksum
from picodfplayer import DFPlayer
import math
import neopixel

xres = 8
yres = 8
pin = 28

i2c = I2C(0, sda=Pin(16), scl=Pin(17))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
wall = neopixel.NeoPixel(machine.Pin(pin), xres * yres)
wall.write()

def scroll_in_screen(screen):
  for i in range (0, oled_width+1, 4):
    for line in screen:
      oled.text(line[2], -oled_width+i, line[1])
    oled.show()
    if i!= oled_width:
      oled.fill(0)

def scroll_out_screen(speed):
  for i in range ((oled_width+1)/speed):
    for j in range (oled_height):
      oled.pixel(i, j, 0)
    oled.scroll(speed,0)
    oled.show()
    
def scroll_screen_in_out(screen):
  for i in range (0, (oled_width+1)*2, 1):
    for line in screen:
      oled.text(line[2], -oled_width+i, line[1])
    oled.show()
    if i!= oled_width:
      oled.fill(0)
    
def mapPixel(x,y):
    if y % 2 == 1 :
        return xres * y + x
    else:
        return xres * y + xres -1 - x

def clignote():
    i = 0
    while True:
        for y in range(yres):
            for x in range(xres):
                if i%2 == 0:
                    r = 255
                    g = 255
                    b = 255
                    wall[mapPixel(x, y)] = (r >> 3, g >> 3, b >> 4)
                else:
                    r = 0
                    g = 0
                    b = 0
                    wall[mapPixel(x, y)] = (r >> 3, g >> 3, b >> 4)
        wall.write()
        i = i +1
        utime.sleep(0.3)
    

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
ssid = 'IIM_Private'
password = 'Creatvive_Lab_2023'
wlan.connect(ssid, password)
sensor = DHT11(Pin(15, Pin.OUT, Pin.PULL_UP))
while True:
    try:
        sensor.measure()
        temp = sensor.temperature
        humidity = sensor.humidity
    except:
        print('Passe pas')
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=48.90&longitude=2.26&hourly=temperature_2m,relativehumidity_2m&current_weather=true&forecast_days=1"
        r = urequests.get(url) # lance une requete sur l'url
        responseData = r.json()
        r.close() # ferme la demande
    except:
        print('Passe pas 2')
    
    screen1 = [[0, 0 , 'Courbevoie'], [0, 16, str(responseData['current_weather']['temperature']) + 'Degres'], [0, 32, 'Humidite : '], [0, 48, str(round(sum(responseData['hourly']['relativehumidity_2m']) / len(responseData['hourly']['relativehumidity_2m']), 2)) + ' %']]
    screen2 = [[0, 0 , 'Piece'], [0, 16, str(temp) + 'Degres'], [0, 32, 'Humidite : '], [0, 48, str(humidity) + ' %']]
    screen3 = [[0, 0 , 'Delta'], [0, 16, str((temp - responseData['current_weather']['temperature'])) + 'Degres'], [0, 32, 'Humidite : '], [0, 48, str((humidity - round(sum(responseData['hourly']['relativehumidity_2m']) / len(responseData['hourly']['relativehumidity_2m']), 2))) + ' %']]
    scroll_screen_in_out(screen1)
    scroll_screen_in_out(screen2)
    scroll_screen_in_out(screen3)
    if responseData['current_weather']['weathercode'] <= 3:
        for y in range(yres):
            for x in range(xres):
                r = 249
                g = 100
                b = 28
                wall[mapPixel(x, y)] = (r >> 3, g >> 3, b >> 4)
        wall.write()
    elif responseData['current_weather']['weathercode'] > 3 and responseData['current_weather']['weathercode'] <= 57:
        for y in range(yres):
            for x in range(xres):
                r = 105
                g = 105
                b =105
                wall[mapPixel(x, y)] = (r >> 3, g >> 3, b >> 4)
        wall.write()
    elif responseData['current_weather']['weathercode'] > 57 and responseData['current_weather']['weathercode'] <= 67:
        for y in range(yres):
            for x in range(xres):
                r = 30
                g = 144
                b = 255
                wall[mapPixel(x, y)] = (r >> 3, g >> 3, b >> 4)
        wall.write()
    elif responseData['current_weather']['weathercode'] > 67 and responseData['current_weather']['weathercode'] <= 86:
        for y in range(yres):
            for x in range(xres):
                r = 255
                g = 255
                b = 255
                wall[mapPixel(x, y)] = (r >> 3, g >> 3, b >> 4)
        wall.write()
    elif responseData['current_weather']['weathercode'] > 86:
        clignote()
    utime.sleep(2)
