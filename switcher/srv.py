#FIXME_FLASK from flask import Flask, jsonify, render_template, request, current_app
from datetime import datetime, timedelta
import time
import yaml
import os.path
from threading import Thread, Lock
import copy
import os,sys
import logging
import ptvsd
import thingspeak

import sys
sys.path.insert(0, "../sush_utils")
try:
    from sush_utils import sush_utils
    from reconnect import startReconnect
except ImportError:
    print('No Import')
#https://pypi.python.org/pypi/thingspeak/


try:
    # on Raspberry import proper GPIO Module
    import RPi.GPIO as GPIO
except:
    #Fallback for PC Development without proper GPIO's attached
    import RPi_stub.GPIO as GPIO

#ptvsd.enable_attach("switcher", address = ('0.0.0.0', 3000))
#Enable the below line of code only if you want the application to wait untill the debugger has attached to it
#ptvsd.wait_for_attach()





logger = logging.getLogger('myserver')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('myserver.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh) # FileHandler 
logger.addHandler(ch)
#fixme_flask app = Flask(__name__)


GPIO_RELAIS_ON = GPIO.HIGH
GPIO_RELAIS_OFF = GPIO.LOW


class ThreadSimplePinWorker(Thread):
    def __init__(self, name, logger):
        Thread.__init__(self)
        self.logger = logger
        self.name = name
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
        startTimeString = "21:20"
        endTimeString   = "21:22"
        startTime = datetime.strptime(startTimeString, '%H:%M').time()
        endTime   = datetime.strptime(endTimeString  , '%H:%M').time()
        assert(endTime > startTime)
        relaisPinStatus = GPIO_RELAIS_OFF
        while(1):
            try:
                time.sleep(10)
                now = datetime.now().time() # e.g. datetime.time(20, 39, 46, 477125)
                if (now > startTime) and (now < endTime):
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
                logger.error ("Exception: " + str(e))
        logger.error ("Exiting " + self.name)


if __name__ == "__main__":
    mySushUtils = sush_utils(logger)
    mySushUtils.time_synchronisation_barrier()

    '''
    now = datetime.now().time()
    a = datetime.strptime("20:25", '%H:%M').time()
    assert(a < now)
    b = datetime.strptime("21:25", '%H:%M').time()
    assert(b > now)
    '''

    logger.info("")
    logger.info("####### starting up... #######")

    THREAD_PINWORKER = ThreadSimplePinWorker("SimplePinWorker", logger)
    THREAD_PINWORKER.start()
 
    startReconnect(logger)

    while(True):
        logger.info("Running reduced set of functions" + mySushUtils.getSystemUpTime_string())
        time.sleep(60*60)