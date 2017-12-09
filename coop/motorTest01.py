from datetime import datetime
import time


try:
    # on Raspberry import proper GPIO Module
    import RPi.GPIO as GPIO
except:
    #Fallback for PC Development without proper GPIO's attached
    import RPi_stub.GPIO as GPIO

class stepper:
    def __init__(self):
        self._PINNUM_ENABLE = 12
        self._PINNUM_PULSE = 16
        self._PINNUM_DIRECTION = 18
        self._PINNUM_SWITCH1 = 37
        self._PIN_ENABLE_ON = GPIO.LOW
        self._PIN_ENABLE_OFF = GPIO.HIGH
        self._INPUT_ACTIVATED = True
        GPIO.setmode(GPIO.BOARD) # Set the board mode to numbers pins by physical location
        GPIO.setup(self._PINNUM_ENABLE, GPIO.OUT) 
        GPIO.setup(self._PINNUM_PULSE, GPIO.OUT) 
        GPIO.setup(self._PINNUM_DIRECTION, GPIO.OUT) 
        GPIO.setup(self._PINNUM_SWITCH1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
        GPIO.output(self._PINNUM_ENABLE, self._PIN_ENABLE_OFF)
        GPIO.output(self._PINNUM_PULSE, GPIO.LOW)
        GPIO.output(self._PINNUM_DIRECTION, GPIO.LOW)

    def move_steps(self, stepCount = 6400, sleepTime = 0.00001, reverse = False):
        try:
            GPIO.output(self._PINNUM_ENABLE, self._PIN_ENABLE_ON)
            if reverse:
                GPIO.output(self._PINNUM_DIRECTION, GPIO.HIGH)
            else:
                GPIO.output(self._PINNUM_DIRECTION, GPIO.LOW)
            for i in range(stepCount):
                GPIO.output(self._PINNUM_PULSE, GPIO.LOW)
                time.sleep(sleepTime)
                GPIO.output(self._PINNUM_PULSE, GPIO.HIGH)
                time.sleep(sleepTime)
        finally:
            GPIO.output(self._PINNUM_ENABLE, self._PIN_ENABLE_OFF)


    def move_to_switch1(self, sleepTime = 0.00001, reverse = False):
        try:
            GPIO.output(self._PINNUM_ENABLE, self._PIN_ENABLE_ON)
            pinDebounceMax = 1000
            if reverse:
                GPIO.output(self._PINNUM_DIRECTION, GPIO.HIGH)
            else:
                GPIO.output(self._PINNUM_DIRECTION, GPIO.LOW)
            pinDebounceCount = 0
            while(True):
                GPIO.output(self._PINNUM_PULSE, GPIO.LOW)
                time.sleep(sleepTime)
                GPIO.output(self._PINNUM_PULSE, GPIO.HIGH)
                time.sleep(sleepTime)
                if self._INPUT_ACTIVATED == GPIO.input(self._PINNUM_SWITCH1):
                    pinDebounceCount = pinDebounceCount +1
                else:
                    pinDebounceCount = 0
                if (pinDebounceCount > pinDebounceMax):
                    return
        finally:
            GPIO.output(self._PINNUM_ENABLE, self._PIN_ENABLE_OFF)



    def rotateFull(self, rounds = 1):
        self.move_steps(stepCount = 6400 * rounds)



if __name__ == "__main__":
    myStepper = stepper()
    myStepper.move_to_switch1()


