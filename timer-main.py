import RPi.GPIO as GPIO
import time

import board
import digitalio
import adafruit_character_lcd.character_lcd as character_lcd

GPIO.setmode(GPIO.BCM)


PANICK_BUTTON_PIN = 26
LIMIT_SWITCH = 14
BUZZER_PIN = 12
SAFE_BUTTON_PIN = 16

GREEN_LIGHT_PIN = 5
YELLOW_LIGHT_PIN = 6
RED_LIGHT_PIN = 0

# LCD pin configuration
lcd_rs = digitalio.DigitalInOut(board.D25)
lcd_en = digitalio.DigitalInOut(board.D24)
lcd_d7 = digitalio.DigitalInOut(board.D22)
lcd_d6 = digitalio.DigitalInOut(board.D18)
lcd_d5 = digitalio.DigitalInOut(board.D17)
lcd_d4 = digitalio.DigitalInOut(board.D23)
lcd_backlight = digitalio.DigitalInOut(board.D2)

lcd_columns = 16
lcd_rows = 2

TIMER_BUZZ_INTERVAL = 5
TIMER_PANIC = 3

# 14 minutes operating time
TIME_OUT_LIMIT = 10

REFRESH_FREQUENCY = 0.5


#	-----	SETUP	-----

GPIO.setup(PANICK_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SAFE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LIMIT_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(BUZZER_PIN, GPIO.OUT)

GPIO.setup(GREEN_LIGHT_PIN, GPIO.OUT)

# Initialize the LCD
lcd = character_lcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)

def status_good():
	GPIO.output(GREEN_LIGHT_PIN, GPIO.HIGH)

def print_msg(string):
    lcd.clear()
    lcd.message = string

def reminder():
	GPIO.output(GREEN_LIGHT_PIN, GPIO.LOW)
	print("in buzzer interval")
	print_msg("hold green \n button")
	GPIO.output(BUZZER_PIN, GPIO.HIGH)
	GPIO.output(YELLOW_LIGHT_PIN, GPIO.HIGH)
	time.sleep(0.2)
	GPIO.output(BUZZER_PIN, GPIO.LOW)
	GPIO.output(YELLOW_LIGHT_PIN, GPIO.LOW)

def panic():
	print("!!! Sending PANIC alert !!!")
	GPIO.output(GREEN_LIGHT_PIN, GPIO.LOW)   
	GPIO.output(BUZZER_PIN, GPIO.HIGH)
	start_time = time.time()
	print_msg("!! PANIC !! \n") 
    
	while True:

		GPIO.output(RED_LIGHT_PIN, GPIO.HIGH)
		time.sleep(0.1)
		GPIO.output(RED_LIGHT_PIN, GPIO.LOW)

		if not GPIO.input(SAFE_BUTTON_PIN):
			print("Canceling PANIC request")
			print_msg("Reversed \n PANIC CALL")
			break
    	

    

#start_time = 0


try:
	while True:
	# Button is pressed when input is LOW
		if GPIO.input(LIMIT_SWITCH):
		
			print("Box Opened....")

			start_time = time.time()
			current_time = time.time()

			status_good()

			# Looping until time out 
			while (current_time-start_time) < TIME_OUT_LIMIT:
			
				print("in main loop")
				print_msg("Status: Normal \n")

				status_good()
			
				if (current_time-start_time) > TIMER_BUZZ_INTERVAL:
					print("in buzzer interval")
					
					start_time = time.time()
					current_time = time.time()
					while (current_time-start_time) < TIMER_PANIC:
					
						reminder()
					
						if not GPIO.input(SAFE_BUTTON_PIN):
							print("SAFE PIN")
							# Reset start time to reflect that user is still active
							start_time = time.time()
							break
							
						if GPIO.input(PANICK_BUTTON_PIN):
							panic()
						
						current_time = time.time()
						time.sleep(REFRESH_FREQUENCY)
					
					if (current_time-start_time) >= TIMER_PANIC:
						panic()
						
				# If panic button is pressed, send panic signal to response
				if GPIO.input(PANICK_BUTTON_PIN):
					panic()
				
				current_time = time.time()
				GPIO.output(BUZZER_PIN, GPIO.LOW)   
				
				time.sleep(REFRESH_FREQUENCY)

			
			
			#print_msg("Time out \nplease close box")
			#print("timeout reached, please close the box")

			time.sleep(0.1)
        
except KeyboardInterrupt:
	GPIO.cleanup() 
