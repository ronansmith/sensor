import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(7,GPIO.OUT)
print "LED on"
GPIO.output(7,GPIO.HIGH)
time.sleep(1)
print "LED off"
GPIO.output(7,GPIO.LOW)
GPIO.cleanup()
