import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)


BUTTON_PIN = 17
LIMIT_SWITCH = 14

TIMER_BUZZ_INTERVAL = 120
TIMER_PANICK = 10

# 14 minutes operating time
TIME_OUT_LIMIT = 840


GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LIMIT_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)

start_time = 0


try:
    while True:
        # Button is pressed when input is LOW
        if not GPIO.input(LIMIT_SWITCH):
            print("Box Opened....")

            start_time = time.time()

            current_time = time.time()

            # Looping until time out 
            while (current_time-start_time) < TIME_OUT_LIMIT:

                # If panic button is pressed, send panic signal to response
                if not GPIO.input(LIMIT_SWITCH):
                    print("!!! Sending PANIC alert !!!")

                

            


        time.sleep(0.1)
        
except KeyboardInterrupt:
    GPIO.cleanup() 