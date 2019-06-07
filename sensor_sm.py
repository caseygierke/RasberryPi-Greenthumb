# sensor_sm.py

import RPi.GPIO as GPIO
import time
import datetime

#GPIO SETUP
channel = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)

# let us know when the pin goes hi or low
GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300) 

# assign function to GPIO PIN, Run function on change
#GPIO.add_event_callback(channel, callback) 

report = ''
	
if GPIO.input(channel):
	print "No Water Detected!"
	report = 'dry'
else:
	print "Water Detected!"
	report = 'wet'

wf = open('sm_result.txt','w')
wf.write(report + ',' + str(datetime.datetime.now()));
wf.close()
