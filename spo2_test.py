import board
import digitalio
import adafruit_character_lcd.character_lcd as character_lcd

import sys
import os
import time
import RPi.GPIO as GPIO
import threading

import csv
import busio
import adafruit_bno055

from adafruit_blinka.microcontroller.bcm283x.pin import Pin
import adafruit_bitbangio as bitbangio

from live_respiratory_depression import monitor_breathing

SCL_PIN = 8
SDA_PIN = 7

i2c = bitbangio.I2C(Pin(SCL_PIN), Pin(SDA_PIN))

sensor = adafruit_bno055.BNO055_I2C(i2c)

start_time = time.time()

def save_to_csv(acc, time, filename):
   if not filename.endswith('.csv'):
      filename+='.csv'
      
   data = [acc, time]
   
   with open(filename, 'a', newline='') as f:
      writer = csv.writer(f)
      writer.writerow(data)



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


def max30102_print_to_lcd():
  max30102.get_heartbeat_SPO2()
  print("SPO2: "+str(max30102.SPO2)+"% \nH-rate: "+str(max30102.heartbeat)+"bpm ")
  #print_msg("SPO2: "+str(max30102.SPO2)+"% \nH-rate: "+str(max30102.heartbeat)+"bpm ") 
  #print_msg("H-rate is: "+str(max30102.heartbeat)+"Times/min")
  time.sleep(1)

if __name__ == "__main__":
    try:
        max30102_setup()
        while True:
            max30102_print_to_lcd()

            gravity = [
              [sensor.gravity[2]]
            ]
              
            lin_motion = [
              [sensor.linear_acceleration[2]]
            ]

            curr_time = time.time() - start_time

            if sensor.linear_acceleration[2] > 0.12:
            
              print(f"Reading: {lin_motion}C")
            
            save_to_csv(sensor.linear_acceleration[0], curr_time, 'x-axis')
            save_to_csv(sensor.linear_acceleration[1], curr_time, 'y-axis')
            save_to_csv(sensor.linear_acceleration[2], curr_time, 'z-axis')

            monitor_breathing()

    except KeyboardInterrupt:
       print("exiting...")
