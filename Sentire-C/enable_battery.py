#!/usr/bin/python2
# This is run immediatly upon power up to enable the battery backup


import time
import RPi.GPIO as GPIO

# using GPIO numbering
GPIO.setmode(GPIO.BOARD)

#set up logging
import logging
logger = logging.getLogger('power')
hdlr = logging.FileHandler('/home/owapp/power.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

#setting up power supply pin for battery backup
GPIO.setup(38, GPIO.OUT)
GPIO.output(38, True)

time.sleep(10)
logger.info('Started the system successfully (Power GPIO activated 10 seconds ago)')

