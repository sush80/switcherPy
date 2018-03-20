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
    from sush_utils import getSystemUpTime_hours, getSystemUpTime_seconds, getSystemUpTime_string
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




YAML_FIELD_UID = "UID"
YAML_FIELD_ACTIVE = "active"
YAML_FIELD_STARTTIME = "startTime"
YAML_FIELD_STOPTIME = "stopTime"
YAML_TRUE = "true"
YAML_FALSE = "false"



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
logger.addHandler(fh) # FileHandler 
logger.addHandler(ch)
#fixme_flask app = Flask(__name__)

class UserInputException(Exception):
    pass


GPIO_RELAIS_ON = GPIO.HIGH
GPIO_RELAIS_OFF = GPIO.LOW


class GLOBAL_DATA():
    def __init__(self):
        self._mutex = Lock()
        logger.info("GLOBAL_DATA init " + hex(id(self)))
        self._loadYamlFile()
        self._manualOverrideFlag = False
        self._pinIsActiveStatus = False
        self._relaisPinNumber = 12  # pin12 = GPIO-18
        self._ledPinNumber = 16  # pin16 = GPIO-23
        self._temperature = 0
        GPIO.setmode(GPIO.BOARD) # Set the board mode to numbers pins by physical location
        GPIO.setup(self._relaisPinNumber, GPIO.OUT) # Set pin mode as output
        GPIO.output(self._relaisPinNumber, GPIO_RELAIS_OFF)
        GPIO.setup(self._ledPinNumber, GPIO.OUT) # Set pin mode as output
        GPIO.output(self._ledPinNumber, GPIO.HIGH)

    '''
    def isManualOverrideFlagSet(self):
        self._mutex.acquire()
        val = copy.copy(self._manualOverrideFlag)
        self._mutex.release()
        return val

    def setOverrideFlag(self, newVal):
        assert(isinstance(newVal, bool))
        self._mutex.acquire()
        self._manualOverrideFlag = newVal
        self._mutex.release()

    def setPinIsActiveStatus(self, newVal):
        assert(isinstance(newVal, bool))
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
            return copy.deepcopy(self._yamlData)
        finally:
            self._mutex.release()
    '''
    
    def _convertToTime(self, aString):
        try:
            return datetime.strptime(aString, '%H:%M').time()
        except:
            raise UserInputException("cannot convert time string " + aString)
        
    def _getYamlFileName(self):
        return 'data.yml'

    def uidStr(self,uid):
        return "UID" + str(uid)
    '''
    def updateConfigFile(self, uid, active="false", start="", end=""):
        self._mutex.acquire()
        logger.info("GLOBAL_DATA updateConfigFile " + hex(id(self)))
        try:
            #with open(g_etYamlFileName(), 'w') as outfile:
            #    yaml.dump(data, outfile, default_flow_style=False)
            if active == YAML_TRUE:
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
                active = YAML_FALSE

            uidStr = self.uidStr(uid)
            self._yamlData[uidStr][YAML_FIELD_ACTIVE] = active
            self._yamlData[uidStr][YAML_FIELD_STARTTIME] = start
            self._yamlData[uidStr][YAML_FIELD_STOPTIME] = end
            
            fName = self._getYamlFileName()
            with open(fName, "w") as f:
                yaml.dump(self._yamlData, f)

        finally:
            self._mutex.release()
        return  ""
    '''
    '''
    def yaml_isActive(self, uid):
        self._mutex.acquire()
        try:
            return self._yamlData[self.uidStr(uid)][YAML_FIELD_ACTIVE] == YAML_TRUE
        finally:
            self._mutex.release()
    '''

    def _processUid(self, uid):
        now = datetime.now()
        tim = now.time()

        [timerIsActive, startTime, stopTime] = self._yaml_info_get(uid)
        if (timerIsActive == True) and (tim >= startTime) and (tim <= stopTime):
            timestring =  now.strftime("%Y-%m-%d %H:%M")
            logger.debug ("Timer " + str(uid) + " is active - " + 
                          timestring +  
                          " - " + str(tim) + 
                          " - " + str(timerIsActive) + 
                          " - " + str(startTime) + 
                          " - " + str(stopTime)  +
                          " - _processUid " + hex(id(self)))
            return True
        return False

    def process(self):
#self._mutex.acquire()
        try:
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
                    GPIO.output(self._relaisPinNumber, GPIO_RELAIS_ON)
                    online_update_SwitchingOn(1)
                else:
                    GPIO.output(self._relaisPinNumber, GPIO_RELAIS_OFF)
                    online_update_SwitchingOn(-1)
        except:
            try:
                logger.error ("process::Errorhandler turning off ...")
                GPIO.output(self._relaisPinNumber, GPIO_RELAIS_OFF)
            except:
                logger.error ("process::Errorhandler turning off failed")
        finally:
            pass
#self._mutex.release()

    def yaml_info_get(self, uid):
        self._mutex.acquire()
        try:
            data = self._yaml_info_get(uid)
            ret = copy.copy(data)
            return ret
        finally:
            self._mutex.release()

    def _yaml_info_get(self, uid):
        active = False
        startTime = ""
        stopTime = ""
        try:
            uidStr = self.uidStr(uid)
            active = self._yamlData[uidStr][YAML_FIELD_ACTIVE] == YAML_TRUE
            startTime = self._convertToTime(self._yamlData[uidStr][YAML_FIELD_STARTTIME])
            stopTime = self._convertToTime(self._yamlData[uidStr][YAML_FIELD_STOPTIME])     
        except Exception as e:
            logger.error("_yaml_info_get: " + str(e))
            active = False
            startTime = ""
            stopTime = ""
        return [active, startTime, stopTime]

    def _initYamlFile(self):
        logger.debug("creating default yaml file")
        fName = self._getYamlFileName()
        self._yamlData = dict(
                UID0 = dict(
                    UID = '0',
                    active = YAML_FALSE,
                    startTime = '00:00',
                    stopTime = '00:00')
                ,
                UID1 = dict(
                    UID = '1',
                    active = YAML_FALSE,
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




'''
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
'''

'''
with open("DO_NOT_ADD_TO_GIT_THINGSPEAK_CHANNEL_WRITE_KEY.txt", "r") as myfile:
    THINGSPEAK_CHANNEL_write_key=myfile.readlines()
    print(THINGSPEAK_CHANNEL_write_key)

#THINGSPEAK_CHANNEL = thingspeak.Channel(id=380347,write_key=THINGSPEAK_CHANNEL_write_key)

def online_update_temperature_uptime(temperature, uptime_hours):

    try:
        # THINGSPEAK_CHANNEL.update({1:temperature,4:uptime_hours})
        logger.debug("uptime report: " + str(uptime_hours))
    except Exception as e:
        pass
        logger.error("could not update online data " + str(e))
def online_update_SwitchingOn(newVal):
    try:
        # THINGSPEAK_CHANNEL.update({2:newVal})
        pass
    except Exception as e:
        pass
        logger.error("could not update online data " + str(e))
def online_update_Bootup(temperature):
    try:
        # THINGSPEAK_CHANNEL.update({1:temperature, 3:1})
        pass
    except Exception as e:
        pass
        logger.error("could not update online data " + str(e))
'''

''' #fixme_flask 
@app.route("/index.html", methods=['GET', 'POST'])
def index_html():
    #logger.debug("index_html")    
    #if request.form.get('test'):
    #    logger.debug("test found")
    return ROOT()


@app.route("/", methods=['GET', 'POST'])
def ROOT():
    current_status_active = "<empty>"
    errorString = ""
    force_override_checked = ""
    upTimeString = ""
    temperature = ""
    _GDATA = current_app._get_current_object().config["_GDATA"]
    try:
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
        else:
            current_status_active = "off"
        
        if _GDATA.isManualOverrideFlagSet():
            force_override_checked = "checked"

        upTimeString = getSystemUpTime_string()
        temperature = str(_GDATA.getTemperature())

    except UserInputException as e:
        logger.error("Caugth UserInputException " + str(e))
        errorString = "UIE:" + str(e)
    except Exception as e:
        logger.error("Caugth Exception " + str(e))
        errorString = "E:" + str(e)
    try:
        templateData = {
            'error_text' : errorString,
            'title' : 'Switcher!',
            'time': timeString,
            'uid0_active': yamlData["UID0"][YAML_FIELD_ACTIVE],
            'uid0_start' : yamlData["UID0"][YAML_FIELD_STARTTIME],
            'uid0_stop'  : yamlData["UID0"][YAML_FIELD_STOPTIME],
            'uid1_active': yamlData["UID1"][YAML_FIELD_ACTIVE],
            'uid1_start' : yamlData["UID1"][YAML_FIELD_STARTTIME],
            'uid1_stop'  : yamlData["UID1"][YAML_FIELD_STOPTIME],
            'current_status_active' : current_status_active,
            'force_override_checked' :force_override_checked,
            'temperature' : temperature,
            'upTime' : upTimeString
        }
        return render_template('main_jinja2_template.html', **templateData)
    except Exception as e:
        logger.error("could not render index.html: " + str(e))
        try:
            templateData = {
                    'tbd' : ""
                }
            return render_template('error.html', **templateData)
        except:
            logger.error("could not render error.html")


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
'''

class ThreadPinWorker (Thread):
    def __init__(self, threadID, name, gdata):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.pinActiveCurrent = False
        self.gdata = gdata
    

    def run(self):
        logger.debug ("Starting " + self.name)
        ledOn = True
        while(1):
            time.sleep(10)
            self.gdata.process()
            if ledOn:
                GPIO.output(self.gdata._ledPinNumber, GPIO.HIGH)
                ledOn = False
            else:
                GPIO.output(self.gdata._ledPinNumber, GPIO.LOW)
                ledOn = True

        logger.debug ("Exiting " + self.name)

'''
class Thread_Temperature_Uptime (Thread):
    def __init__(self, threadID, name, gdata):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name    
        self.gdata = gdata

    def run(self):
        logger.debug ("Starting " + self.name)
        while(1):
            temperature = readTemperature()
            self.gdata.setTemperature(temperature)
            uptime_hours = getSystemUpTime_hours()
            online_update_temperature_uptime(temperature, uptime_hours)
            time.sleep(60*60)
        logger.debug ("Exiting " + self.name)
'''
if __name__ == "__main__":
    #start threads
    while(True):
        now = datetime.now()
        if now.year > 2017:
            break
        logger.warning("local clock not up to date, postponing start of server:" + str(now))
        time.sleep(10)

    logger.info("")
    logger.info("####### starting up... #######")
    GDATA = GLOBAL_DATA()

    # that is the ONLY ! Place where the flask app can access global data !
    #fixme_flask app.config.update(_GDATA = GDATA)
    #GDATA.setTemperature(readTemperature()) # set values
    logger.info("Data intialized -> starting threads.")

    THREAD_PINWORKER = ThreadPinWorker(1, "PinWorker", GDATA)
    THREAD_PINWORKER.start()
    #THREAD_TEMPERATURE_UPTIME = Thread_Temperature_Uptime(2, "Thread_Temperature_Uptime", GDATA)
    #THREAD_TEMPERATURE_UPTIME.start()

    #online_update_Bootup(readTemperature())# requires valid temperature
    GDATA.process()

    startReconnect(logger)


    #fixme_flask logger.info("Will start flask now")
    
    #use_reloader = False is to prevent this file to be started multiple times, resulting in multiple threads
    #                     and duplicated data structurs
    #fixme_flask app.run(host='0.0.0.0', port=5000, debug=True,use_reloader=False)

    while(True):
        logger.info("Running without flask " + getSystemUpTime_string())
        time.sleep(60*60)