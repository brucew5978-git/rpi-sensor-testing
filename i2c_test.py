import board
import busio
import adafruit_bno055

import csv
import time

def save_to_csv(acc, time, filename):
   if not filename.endswith('.csv'):
      filename+='.csv'
      
   data = [acc, time]
   
   with open(filename, 'a', newline='') as f:
      writer = csv.writer(f)
      writer.writerow(data)

i2c = busio.I2C(board.SCL, board.SDA)

sensor = adafruit_bno055.BNO055_I2C(i2c)

start_time = time.time()

print("Sensor Data")

while True: 
  gravity = [
    #[sensor.gravity[0]],
    #[sensor.gravity[1]],
    [sensor.gravity[2]]
    ]
    
  lin_motion = [
    #[sensor.linear_acceleration[0]],
    #[sensor.linear_acceleration[1]],
    [sensor.linear_acceleration[2]]
    ]
  
  curr_time = time.time() - start_time
    
  #if sensor.linear_acceleration[0] > 0.12 or sensor.linear_acceleration[1] > 0.12 or sensor.linear_acceleration[2] > 0.12:
  if sensor.linear_acceleration[2] > 0.12:
  
    print(f"Reading: {lin_motion} {curr_time}C")
  
  save_to_csv(sensor.linear_acceleration[0], curr_time, 'x-axis')
  save_to_csv(sensor.linear_acceleration[1], curr_time, 'y-axis')
  save_to_csv(sensor.linear_acceleration[2], curr_time, 'z-axis')
  time.sleep(0.01)
