#!/usr/bin/python

import time
import RPi.GPIO as GPIO
import subprocess

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

# set up gpio 8 to pull up
GPIO.setup(40, GPIO.IN, pull_up_down=GPIO.PUD_UP)


interval = 1
batcounter = 0
batstatus = GPIO.input(40)
runcounter = 0
duration = 300

while runcounter <= duration:
        #run counter is used to stop the loop after 5 minutes, we then rely on cron to restart the process.
        #(It prevents crashed scripts)
        runcounter += 1
        time.sleep(interval)

        newstatus = GPIO.input(40)

        # checking if status changed from before
        if (newstatus != batstatus):
                batstatus = newstatus
                if (newstatus == True):
                        logger.info('Switched to battery power (GPIO PIN 40 HIGH)')

                else:
                        logger.info('Switched to mains power (GPIO PIN 40 LOW)')

        #incrementing or resetting counter (used for the battery disconnect)
        if (newstatus == True):
                batcounter += 1
        else:
                batcounter = 0

        # poweroff after 10 intervals on battery
        if (batcounter >= 10):
                logger.info('Powering off due to battery limit')

                # calling "reboot" instead of "poweroff" because that should also set pin 7 to be LOW and
                # disconnect battery, but If power returns during the shutdown process it would boot as normal.
                subprocess.call("reboot", shell=True)
                exit(0)