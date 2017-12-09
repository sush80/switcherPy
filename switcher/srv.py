from flask import Flask, jsonify, render_template, request
from datetime import datetime
import time
import yaml
import os.path
from threading import Thread, Lock
import copy
import os,sys
import logging
import ptvsd
import thingspeak
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
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
# no file handler for now: logger.addHandler(fh)
logger.addHandler(ch)

app = Flask(__name__)

class UserInputException(Exception):
    pass




class GLOBAL_DATA():
    def __init__(self):
        self._mutex = Lock()
        self._loadYamlFile()
        self._manualOverrideFlag = False
        self._pinIsActiveStatus = False
        self._relaisPinNumber = 12  # pin12 = GPIO-18
        self._temperature = 0
        GPIO.setmode(GPIO.BOARD) # Set the board mode to numbers pins by physical location
        GPIO.setup(self._relaisPinNumber, GPIO.OUT) # Set pin mode as output
        GPIO.output(self._relaisPinNumber, GPIO.LOW)

    def isManualOverrideFlagSet(self):
        self._mutex.acquire()
        val = copy.copy(self._manualOverrideFlag)
        self._mutex.release()
        return val

    def setOverrideFlag(self, newValue):
        self._mutex.acquire()
        self._manualOverrideFlag = newValue
        self._mutex.release()

    def setPinIsActiveStatus(self, newVal):
        self._mutex.acquire()
        self._pinIsActiveStatus = newVal
        self._mutex.release()

    def getPinIsActiveStatus(self):
        self._mutex.acquire()
        val = copy.copy(self._pinIsActiveStatus)
        self._mutex.release()
        return val

    def setTemperature(self, newVal):
        self._mutex.acquire()
        self._temperature = newVal
        self._mutex.release()

    def getTemperature(self):
        self._mutex.acquire()
        _temperature = copy.copy(self._temperature)
        self._mutex.release()
        return _temperature

    def yaml_data_get(self):
        self._mutex.acquire()
        try:
            return copy.copy(self._yamlData)
        finally:
            self._mutex.release()

    def _convertToTime(self, aString):
        try:
            return datetime.strptime(aString, '%H:%M').time()
        except:
            raise UserInputException("cannot convert time string " + aString)
        
    def _getYamlFileName(self):
        return 'data.yml'

    def updateConfigFile(self, uid, active="false", start="", end=""):
        self._mutex.acquire()
        try:
            #with open(g_etYamlFileName(), 'w') as outfile:
            #    yaml.dump(data, outfile, default_flow_style=False)
            if active == "true":
                try:
                    _start = self._convertToTime(start)
                    #logger.debug("start time is valid")
                    _end = self._convertToTime(end)
                    #logger.debug("end time is valid")
                    if _end <= _start:
                        raise UserInputException("End Time must be greater than Start Time")
                except ValueError:
                    raise UserInputException("Error on time conversion")
            else:
                active = "false"

            uidStr = "UID" + str(uid)
            self._yamlData[uidStr]["active"] = active
            self._yamlData[uidStr]["startTime"] = start
            self._yamlData[uidStr]["stopTime"] = end
            
            fName = self._getYamlFileName()
            with open(fName, "w") as f:
                yaml.dump(self._yamlData, f)

        finally:
            self._mutex.release()
        return 


    def yaml_isActive(self, uid):
        self._mutex.acquire()
        try:
            uidStr = "UID" + str(uid)
            return self._yamlData[uidStr]["active"] == "true"
        finally:
            self._mutex.release()


    def _processUid(self, uid):
        now = datetime.now()
        if now.year < 2017:
            logger.warning("local clock not up to date, skipping _processUid: " + str(now))
            return False
        tim = now.time()

        [timerIsActive, startTime, stopTime] = self._yaml_info_get(uid)
        if timerIsActive and (tim >= startTime) and (tim <= stopTime):
            logger.debug ("Timer " + str(uid) + " is active")
            return True
        return False

    def process(self):
        self._mutex.acquire()
        pinActiveNew = False
        for uid in range(2):
            if self._processUid(uid):
                pinActiveNew = True
        if self._manualOverrideFlag:
            logger.debug ("Override Flag set, will switch")
            pinActiveNew = True
        if self._pinIsActiveStatus != pinActiveNew:
            self._pinIsActiveStatus = pinActiveNew
            logger.debug ("switching pin to new: " + str(self._pinIsActiveStatus))
            if self._pinIsActiveStatus:
                GPIO.output(self._relaisPinNumber, GPIO.HIGH)
                online_update_SwitchingOn(1)
            else:
                GPIO.output(self._relaisPinNumber, GPIO.LOW)
                online_update_SwitchingOn(-1)
        self._mutex.release()

    def yaml_info_get(self, uid):
        self._mutex.acquire()
        try:
            return self._yaml_info_get(uid)
        finally:
            self._mutex.release()

    def _yaml_info_get(self, uid):
        uidStr = "UID" + str(uid)
        active = self._yamlData[uidStr]["active"] == "true"
        try:
            startTime = self._convertToTime(self._yamlData[uidStr]["startTime"])
            stopTime = self._convertToTime(self._yamlData[uidStr]["stopTime"])
        except:
            startTime = ""
            stopTime = ""
        return [active, startTime, stopTime]

    def _initYamlFile(self):
        logger.debug("creating default yaml file")
        fName = self._getYamlFileName()
        self._yamlData = dict(
                UID0 = dict(
                    UID = '0',
                    active = 'false',
                    startTime = '00:00',
                    stopTime = '00:00')
                ,
                UID1 = dict(
                    UID = '1',
                    active = 'false',
                    startTime = '00:00',
                    stopTime = '00:00')
                )
        with open(fName, "w") as f:
            yaml.dump(self._yamlData, f)


    def _loadYamlFile(self):
        fName = self._getYamlFileName()
        if not os.path.isfile(fName) :
            self._initYamlFile()
        with open(fName) as f:
            # use safe_load instead load
            self._yamlData = yaml.safe_load(f)


_GDATA = GLOBAL_DATA()


def readTemperature():
    try:
        file = open('/sys/bus/w1/devices/28-0317019e9eff/w1_slave')
        filecontent = file.read()
        file.close()

        stringvalue = filecontent.split("\n")[1].split(" ")[9]
        temperature = float(stringvalue[2:]) / 1000
        retVal = '%6.2f' % temperature 
        return(retVal)
    except Exception as e:
        logger.error("could not read temperature: " + str(e))
        return 0.0





with open("DO_NOT_ADD_TO_GIT_THINGSPEAK_CHANNEL_WRITE_KEY.txt", "r") as myfile:
    THINGSPEAK_CHANNEL_write_key=myfile.readlines()
    print(THINGSPEAK_CHANNEL_write_key)

THINGSPEAK_CHANNEL = thingspeak.Channel(id=380347,write_key=THINGSPEAK_CHANNEL_write_key)

def online_update_temperature():
    temp = _GDATA.getTemperature()
    try:
        THINGSPEAK_CHANNEL.update({1:temp})
    except Exception as e:
        logger.error("could not update online data " + str(e))
def online_update_SwitchingOn(newVal):
    try:
        THINGSPEAK_CHANNEL.update({2:newVal})
    except Exception as e:
        logger.error("could not update online data " + str(e))
def online_update_Bootup():
    temp = _GDATA.getTemperature()
    try:
        THINGSPEAK_CHANNEL.update({1:temp, 3:1})
    except Exception as e:
        logger.error("could not update online data " + str(e))
       


@app.route("/index.html", methods=['GET', 'POST'])
def index_html():
    #logger.debug("index_html")    
    #if request.form.get('test'):
    #    logger.debug("test found")
    return ROOT()


@app.route("/", methods=['GET', 'POST'])
def ROOT():
    current_status_active = "off"
    errorString = ""
    force_override_checked = ""
    try:
        global _GDATA
        logger.debug("root html")
        now = datetime.now()
        timeString = now.strftime("%Y-%m-%d %H:%M")
        yamlData = _GDATA.yaml_data_get()

        if request.form.get('action') == "setOverrideFlag":
            if request.form.get('active'):
                logger.debug(" override ON ")
                _GDATA.setOverrideFlag(True)
            else:
                logger.debug(" override off ")
                _GDATA.setOverrideFlag(False)
        elif request.form.get('action') == "setAlarmTimes":
            startTime = request.form.get('start')
            stopTime = request.form.get('stop')
            active = request.form.get('active')
            UID = request.form.get('UID')
            logger.debug("setAlarmTimes: " +str(UID) + " " + str(active) + " " + str(startTime) + " " + str(stopTime))
            errorString = _GDATA.updateConfigFile(uid = UID,active = active, start = startTime, end = stopTime)
        else:
            logger.debug("no action")
        
        _GDATA.process()

        if _GDATA.getPinIsActiveStatus():
            current_status_active = "on"
        
        if _GDATA.isManualOverrideFlagSet():
            force_override_checked = "checked"
    except UserInputException as e:
        logger.error("Caugth UserInputException " + str(e))
        errorString = str(e)
    except Exception as e:
        logger.error("Caugth Exception " + str(e))
        errorString = str(e)
        
    templateData = {
        'error_text' : errorString,
        'title' : 'Switcher!',
        'time': timeString,
        'uid0_active': yamlData["UID0"]["active"],
        'uid0_start' : yamlData["UID0"]["startTime"],
        'uid0_stop'  : yamlData["UID0"]["stopTime"],
        'uid1_active': yamlData["UID1"]["active"],
        'uid1_start' : yamlData["UID1"]["startTime"],
        'uid1_stop'  : yamlData["UID1"]["stopTime"],
        'current_status_active' : current_status_active,
        'force_override_checked' :force_override_checked,
        'temperature' : str(_GDATA.getTemperature())
    }
    return render_template('main_jinja2_template.html', **templateData)


@app.route("/timepicker.html", methods=['GET'])
def timepicker():
    uid = request.args.get('UID')
    if uid == None:
        raise Exception("uid == none")

    templateData = {
        'UID' : str(uid),
        'start' : request.args.get('start'),
        'stop' : request.args.get('stop')
    }
    return render_template('timepicker.html', **templateData)


@app.route('/reset.html')
def reset_html():
    templateData = {
        'tbd' : ""
    }
    return render_template('reset.html',**templateData)

@app.route('/doReset')
def doReset():
    os.system("sudo reboot")


class ThreadPinWorker (Thread):
    def __init__(self, threadID, name):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.pinActiveCurrent = False
    

    def run(self):
        global _GDATA
        logger.debug ("Starting " + self.name)
        while(1):
            time.sleep(10)
            _GDATA.process()
        logger.debug ("Exiting " + self.name)


class ThreadTemperature (Thread):
    def __init__(self, threadID, name):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name    

    def run(self):
        global _GDATA
        logger.debug ("Starting " + self.name)
        while(1):
            temperature = readTemperature()
            _GDATA.setTemperature(temperature)
            online_update_temperature()
            time.sleep(60*60)
        logger.debug ("Exiting " + self.name)

if __name__ == "__main__":
    #start threads
    THREAD_PINWORKER = ThreadPinWorker(1, "PinWorker")
    THREAD_PINWORKER.start()
    THREAD_TEMPERATURE = ThreadTemperature(1, "Temperature")
    THREAD_TEMPERATURE.start()

    _GDATA.setTemperature(readTemperature()) # set values
    online_update_Bootup()# requires valid temperature
    _GDATA.process()
    
    app.run(host='0.0.0.0', port=5000, debug=True)