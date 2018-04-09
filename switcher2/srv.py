from flask import Flask, jsonify, render_template, request, current_app
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
import copy

import sys

from sush_utils.sush_utils import system_uptime


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




class SharedData(object):

    class __SharedData(object):
        def __init__(self):
            self._lock = Lock()
            self._timer_start = self._time_from_string("20:59")
            self._timer_end = self._time_from_string("21:00")
            self._cfg_file_name = "FIXME"
        
        # Format HH:MM
        def _time_from_string(self, timer):
            return datetime.strptime(timer, '%H:%M').time()

        # Format HH:MM
        def _time_to_string(self, timer):
            return timer.strftime("%H:%M")
        
        def timer_set(self, start, end):
            with self._lock:
                if isinstance(start, "") and isinstance(end, ""):
                    start = self._time_from_string(start)
                    end = self._time_from_string(end)
                self._timer_start = start
                self._timer_end = end
                #FIXME STORE TO FILE
            
        def timer_get(self):
            with self._lock:
                start = copy.deepcopy(self._timer_start)
                end = copy.deepcopy(self._timer_end)
                return [start, end]
            
        def timer_get_as_string(self):
            [start, end] = self.timer_get()
            return [self._time_to_string(start), self._time_to_string(end)] 

    __instance = None
    
    def __init__(self):
        if not SharedData.__instance:
            SharedData.__instance = SharedData.__SharedData()
    def __getattr__(self, name):
        return getattr(self.__instance, name)



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
        while(1):
            try:
                time.sleep(10)
                [startTime , endTime] = self._sharedData.timer_get()
                now = datetime.now().time() # e.g. datetime.time(11, 39, 30, 155284)
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


    THREAD_PINWORKER = ThreadSimplePinWorker("SimplePinWorker", logger, SharedData())
    THREAD_PINWORKER.start()
 
    

