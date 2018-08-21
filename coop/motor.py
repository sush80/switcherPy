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

from sush_utils.sush_utils import is_elapsed


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





GPIO_MOTOR_OFF = GPIO.HIGH
GPIO_MOTOR_ON = GPIO.LOW

GPIO_ENDPOS_ACTIVE = True
GPIO_ENDPOS_INACTIVE = False



class ThreadMotor(Thread):
    def __init__(self, name, logger):
        Thread.__init__(self)
        self.logger = logger
        self.name = name
        self._timeout_movement_seconds = 60
        self._pin_motor_up = 12  # pin12 = GPIO-18
        self._pin_motor_down = 16  # pin16 = GPIO-23
        self._pin_endswitch_top = 17 # pin
        self._pin_endswitch_bottom = 18 # pin
        GPIO.setmode(GPIO.BOARD) # Set the board mode to numbers pins by physical location
        GPIO.setup(self._pin_motor_up, GPIO.OUT) 
        GPIO.output(self._pin_motor_up, GPIO_MOTOR_OFF)
        GPIO.setup(self._pin_motor_down, GPIO.OUT) 
        GPIO.output(self._pin_motor_down, GPIO_MOTOR_OFF)
        GPIO.setup(self._pin_endswitch_top, GPIO.IN)
        GPIO.setup(self._pin_endswitch_bottom, GPIO.IN)  


    def _debug_check_endpositions(self):
        while(1):
            a = ("EndPosTop    " + str(GPIO.input(self._pin_endswitch_top)))
            b = ("  EndPosBottom " + str(GPIO.input(self._pin_endswitch_bottom)))
            print( a + b)
            time.sleep(2)


    def move(self, up = True):
        GPIO.output(self._pin_motor_down, GPIO_MOTOR_OFF)
        GPIO.output(self._pin_motor_up, GPIO_MOTOR_OFF)
        
        if up:
            motor_pin = self._pin_motor_up
            endposition_pin = self._pin_endswitch_top
        else:
            motor_pin = self._pin_motor_down
            endposition_pin = self._pin_endswitch_bottom

        GPIO.output(motor_pin, GPIO_MOTOR_ON)
        start_time = time.time() # seconds since epoch
        try:
            while(not is_elapsed(start_time, self._timeout_movement_seconds)):
                #if GPIO.
                #pass 
                self.logger.debug(" ... moving ... ")
                time.sleep(10)
                if GPIO.input(endposition_pin) == GPIO_ENDPOS_ACTIVE:
                    GPIO.output(motor_pin, GPIO_MOTOR_OFF)
                    self.logger.debug("stopped")
                    return
            self.logger.error("Motor Timout")
        finally:
            GPIO.output(motor_pin, GPIO_MOTOR_OFF)


    def run(self):
        self.logger.info ("Starting")
        while(1):
            try:
                time.sleep(10)
            except Exception as e:
                self.logger.error ("Exception: " + str(e))
        self.logger.error ("Exiting " + self.name)


def start_motor(logger):

    logger.info("####### starting up... #######")

    THREAD_MOTOR = ThreadMotor("ThreadMotor", logger)
    #THREAD_MOTOR.start()
    THREAD_MOTOR._debug_check_endpositions()
    

