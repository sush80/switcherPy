from flask import Flask, jsonify, render_template, request
from datetime import datetime
import time
import yaml
import os.path
from threading import Thread, Lock
import copy
import os


app = Flask(__name__)

class GLOBAL_DATA:
    def __init__(self):
        self._mutex = Lock()
        self._loadYamlFile()
        self._manualOverrideFlag = False
        self._pinIsActiveStatus = False

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

    def yaml_data_get(self):
        self._mutex.acquire()
        try:
            return copy.copy(self._yamlData)
        finally:
            self._mutex.release()

    def _convertToTime(self, aString):
        return datetime.strptime(aString, '%H:%M').time()

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
                    print("start time is valid")
                    _end = self._convertToTime(end)
                    print("end time is valid")
                    if _end <= _start:
                        return "start cannot be after end"
                except ValueError:
                    return "Error on time conversion"
            else:
                active = "false"

            uidStr = "UID" + str(uid)
            self._yamlData[uidStr]["active"] = active
            self._yamlData[uidStr]["startTime"] = start
            self._yamlData[uidStr]["endTime"] = end
            
            fName = self._getYamlFileName()
            with open(fName, "w") as f:
                yaml.dump(self._yamlData, f)

        finally:
            self._mutex.release()
        return ""


    def yaml_isActive(self, uid):
        self._mutex.acquire()
        try:
            uidStr = "UID" + str(uid)
            return self._yamlData[uidStr]["active"] == "true"
        finally:
            self._mutex.release()

    def yaml_info_get(self, uid):
        self._mutex.acquire()
        try:
            uidStr = "UID" + str(uid)
            active = self._yamlData[uidStr]["active"] == "true"
            startTime = self._convertToTime(self._yamlData[uidStr]["startTime"])
            endTime = self._convertToTime(self._yamlData[uidStr]["endTime"])
            return [active, startTime, endTime]
        finally:
            self._mutex.release()

    def _initYamlFile(self):
        print("creating default yaml file")
        fName = self._getYamlFileName()
        self._yamlData = dict(
                UID0 = dict(
                    UID = '0',
                    active = 'false',
                    startTime = '00:00',
                    endTime = '00:00')
                ,
                UID1 = dict(
                    UID = '1',
                    active = 'false',
                    startTime = '00:00',
                    endTime = '00:00')
                )
        with open(fName, "w") as f:
            yaml.dump(self._yamlData, f)


    def _loadYamlFile(self):
        self._mutex.acquire()
        try:
            fName = self._getYamlFileName()
            if not os.path.isfile(fName) :
                self._initYamlFile()
            with open(fName) as f:
                # use safe_load instead load
                self._yamlData = yaml.safe_load(f)
        finally:
            self._mutex.release()


_GDATA = GLOBAL_DATA()


@app.route("/index.html")
def index_html():
    global _GDATA
    print("index_html")
    
    return ROOT()



@app.route("/")
def ROOT(errorString  = ''):
    global _GDATA
    print("index html")
    now = datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    yamlData = _GDATA.yaml_data_get()

    if _GDATA.getPinIsActiveStatus():
        current_status_active = "ON"
    else:
        current_status_active = "off"

    if _GDATA.isManualOverrideFlagSet():
        force_override_checked = "checked"
    else:
        force_override_checked = ""
    templateData = {
        'error_text' : errorString,
        'title' : 'Switcher!',
        'time': timeString,
        'uid0_active': yamlData["UID0"]["active"],
        'uid0_start' : yamlData["UID0"]["startTime"],
        'uid0_stop'  : yamlData["UID0"]["endTime"],
        'uid1_active': yamlData["UID1"]["active"],
        'uid1_start' : yamlData["UID1"]["startTime"],
        'uid1_stop'  : yamlData["UID1"]["endTime"],
        'current_status_active' : current_status_active,
        'force_override_checked' :force_override_checked
    }
    return render_template('main_jinja2_template.html', **templateData)


@app.route('/index_onOffDone', methods=['POST'])
def index_report():
    global _GDATA
    print("index_report")
    print(request.args)

    if request.form.get('active'):
        print(" index ON ")
        _GDATA.setOverrideFlag(True)
    else:
        print(" index off ")
        _GDATA.setOverrideFlag(False)
    
    templateData = {
        'tbd' : 'tbd'
    }
    return render_template('action_done.html', **templateData)

@app.route("/timepicker.html", methods=['GET'])
def timepicker():
    now = datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    uid = request.args.get('UID')
    if uid == None:
        raise Exception("uid == none")

    templateData = {
        'UID' : str(uid)
    }
    return render_template('timepicker.html', **templateData)

@app.route('/timepicker_done', methods=['POST'])
def timepicker_report():
    global _GDATA
    print("timepicker_report")
    print(request.args)
    startTime = request.form.get('start')
    endTime = request.form.get('end')
    active = request.form.get('active')
    UID = request.form.get('UID')
    print("timepicker_report" +str(UID) + " " + str(active) + " " + str(startTime) + " " + str(endTime))
    errorText = _GDATA.updateConfigFile(uid = UID,active = active, start = startTime, end = endTime)
    print(" errtxt: " + errorText)
    templateData = {
        'errorText' : errorText
    }
    return render_template('action_done.html', **templateData)


@app.route('/reset.html')
def reset_html():
    templateData = {
        'tbd' : ""
    }
    return render_template('reset.html',**templateData)

@app.route('/doReset')
def doReset():
    os.system("sudo reboot")


class myThread (Thread):
    def __init__(self, threadID, name):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.pinActiveCurrent = False
    
    def processUid(self, uid):
        tim = datetime.now().time()
        [timerIsActive, startTime, endTime] = _GDATA.yaml_info_get(uid)
        if timerIsActive and (tim >= startTime) and (tim <= endTime):
            self.pinActiveNew = True
            print ("Timer " + str(uid) + " is active")

    def run(self):
        global _GDATA
        print ("Starting " + self.name)
        while(1):
            time.sleep(1)
            self.pinActiveNew = False
            for uid in range(2):
                self.processUid(uid)
            if _GDATA.isManualOverrideFlagSet():
                print ("Override Flag set, will switch")
                self.pinActiveNew = True
            if self.pinActiveCurrent != self.pinActiveNew:
                self.pinActiveCurrent = self.pinActiveNew
                _GDATA.setPinIsActiveStatus(self.pinActiveCurrent)
                print ("switching pin to new: " + str(self.pinActiveCurrent))
        print ("Exiting " + self.name)

if __name__ == "__main__":
    thread1 = myThread(1, "PinWorker")
    thread1.start()
    app.run(host='0.0.0.0', port=5000, debug=True)
