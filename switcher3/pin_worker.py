from datetime import datetime, timedelta
import time
import os.path
from threading import Thread, Lock
import copy
import os,sys
import logging
#import ptvsd
#import thingspeak

import sys

from switcher3.shared_data import shared_data


try:
    # on Raspberry import proper GPIO Module
    import RPi.GPIO as GPIO
except:
    #Fallback for PC Development without proper GPIO's attached
    print("WARNING LOADING ONLY GPIO STUB")
    import sush_utils.GPIO_stub as GPIO

#ptvsd.enable_attach("switcher", address = ('0.0.0.0', 3000))
#Enable the below line of code only if you want the application to wait untill the debugger has attached to it
#ptvsd.wait_for_attach()





GPIO_RELAIS_ON = GPIO.HIGH
GPIO_RELAIS_OFF = GPIO.LOW




class ThreadSimplePinWorker(Thread):
    def __init__(self, name, logger, sharedData):
        Thread.__init__(self)
        self.logger = logger
        self.name = name
        self._sharedData = sharedData
        self._relaisPinNumber = 12  # pin12 = GPIO-18
        self._ledPinNumber = 16  # pin16 = GPIO-23
        self._temperature = 0
        GPIO.setmode(GPIO.BOARD) # Set the board mode to numbers pins by physical location
        GPIO.setup(self._relaisPinNumber, GPIO.OUT) # Set pin mode as output
        GPIO.output(self._relaisPinNumber, GPIO_RELAIS_OFF)
        GPIO.setup(self._ledPinNumber, GPIO.OUT) # Set pin mode as output
        GPIO.output(self._ledPinNumber, GPIO.HIGH)
    

    def run(self):
        self.logger.info ("Starting SimplePinWorker")
        relaisPinStatus = GPIO_RELAIS_OFF
        GPIO.output(self._relaisPinNumber, GPIO_RELAIS_OFF)
        [startTime , endTime, active] = self._sharedData.load(returnType = "string")
        self.logger.info(" startTime: " + startTime)
        self.logger.info(" endTime:   " + endTime)
        self.logger.info(" active:    " + active)
        while(1):
            try:
                time.sleep(10)
                new_data_from_file = self._sharedData.has_new_data()
                [startTime , endTime, active] = self._sharedData.load(returnType = "native")
                if new_data_from_file:
                    self.logger.info("New Data from file: " + str(startTime) + " " + str(endTime)  + " " + str(active))
                if (not active):
                    if (GPIO_RELAIS_ON == relaisPinStatus):
                        self.logger.info ("switching off because timer was deactivated")
                        GPIO.output(self._relaisPinNumber, GPIO_RELAIS_OFF)
                        relaisPinStatus = GPIO_RELAIS_OFF
                    continue

                now = datetime.now().time() # e.g. datetime.time(11, 39, 30, 155284)
                if (now >= startTime) and (now < endTime):
                    if GPIO_RELAIS_OFF == relaisPinStatus:
                        self.logger.info ("switching ON")
                        GPIO.output(self._relaisPinNumber, GPIO_RELAIS_ON)
                        relaisPinStatus = GPIO_RELAIS_ON
                    #else: not need to switch on and on again
                else:
                    if GPIO_RELAIS_ON == relaisPinStatus:
                        self.logger.info ("switching off")
                        GPIO.output(self._relaisPinNumber, GPIO_RELAIS_OFF)
                        relaisPinStatus = GPIO_RELAIS_OFF
                    #else: no need to switch off and off again

            except Exception as e:
                self.logger.error ("Exception: " + str(e))
        self.logger.error ("Exiting " + self.name)


def start_pinworker(logger):

    logger.info("####### starting up... #######")

    '''
    now = datetime.now().time()
    a = datetime.strptime("20:25", '%H:%M').time()
    assert(a < now)
    b = datetime.strptime("21:25", '%H:%M').time()
    assert(b > now)
    '''

    sharedData = shared_data()



    THREAD_PINWORKER = ThreadSimplePinWorker("SimplePinWorker", logger, sharedData)
    THREAD_PINWORKER.start()
 
    

