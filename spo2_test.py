import board
import digitalio
import adafruit_character_lcd.character_lcd as character_lcd

import sys
import os
import time
import RPi.GPIO as GPIO
import threading



###
#start of max30102 set up code#
###

# Get the current directory
current_dir = os.path.dirname(os.path.realpath(__file__))

# Walk through all subdirectories and add them to sys.path
for root, dirs, files in os.walk(current_dir):
    sys.path.append(root)

from DFRobot_BloodOxygen_S import *
import smbus

'''
  ctype=1：UART
  ctype=0：IIC
'''
ctype=0
I2C_BUS = 1
I2C_ADDRESS = 0x57


if ctype==0:
  I2C_1       = 0x01               # I2C_1 Use i2c1 interface (or i2c0 with configuring Raspberry Pi file) to drive sensor
  I2C_ADDRESS = 0x57               # I2C device address, which can be changed by changing A1 and A0, the default address is 0x57
  max30102 = DFRobot_BloodOxygen_S_i2c(I2C_1 ,I2C_ADDRESS)
else:
  max30102 = DFRobot_BloodOxygen_S_uart(9600)

def max30102_setup():
  while (False == max30102.begin()):
    print("init fail!")
    time.sleep(1)
  print("start measuring...")
  max30102.sensor_start_collect()
  time.sleep(1)

###
#end of max30102 set up code#
###

lcd_rs = digitalio.DigitalInOut(board.D25)
lcd_en = digitalio.DigitalInOut(board.D24)
lcd_d7 = digitalio.DigitalInOut(board.D22)
lcd_d6 = digitalio.DigitalInOut(board.D18)
lcd_d5 = digitalio.DigitalInOut(board.D17)
lcd_d4 = digitalio.DigitalInOut(board.D23)

lcd_columns = 16
lcd_rows = 2

lcd = character_lcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)

def print_msg(string):
    lcd.message = string


lcd.clear()

def max30102_print_to_lcd():
  max30102.get_heartbeat_SPO2()
  print("SPO2: "+str(max30102.SPO2)+"% \nH-rate: "+str(max30102.heartbeat)+"bpm ")
  print_msg("SPO2: "+str(max30102.SPO2)+"% \nH-rate: "+str(max30102.heartbeat)+"bpm ") 
  #print_msg("H-rate is: "+str(max30102.heartbeat)+"Times/min")
  time.sleep(1)

if __name__ == "__main__":
    try:
        max30102_setup()
        while True:
            max30102_print_to_lcd()
    except KeyboardInterrupt:
       print("exiting...")
