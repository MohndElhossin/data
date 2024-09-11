import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
led = 17
GPIO.setup(led, GPIO.OUT)
#GPIO.OUTPUT(led.GPIO.LOW)

while True:
    GPIO.output(led, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(led, GPIO.LOW)
    time.sleep(1)
     

GPIO.cleanup()