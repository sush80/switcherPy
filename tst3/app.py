from flask import Flask, jsonify, render_template, request
from datetime import datetime
import time
import yaml
import os.path
from threading import Thread, Lock
import copy


app = Flask(__name__)

class GLOBAL_DATA:
    def __init__(self):
        self.mutex = Lock()
        self._loadYamlFile()

    def yaml_data_get(self):
        self.mutex.acquire()
        try:
            return copy.copy(self.yamlData)
        finally:
            self.mutex.release()

    def _convertToTime(self, aString):
        return datetime.strptime(aString, '%H:%M').time()

    def _getYamlFileName(self):
        return 'data.yml'

    def updateConfigFile(self, uid, active="false", start="", end=""):
        self.mutex.acquire()
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
                        return("start cannot be after end")

                    uidStr = "UID" + str(uid)
                    self.yamlData[uidStr]["active"] = active
                    self.yamlData[uidStr]["startTime"] = start
                    self.yamlData[uidStr]["endTime"] = end
                    
                    fName = self._getYamlFileName()
                    with open(fName, "w") as f:
                        yaml.dump(self.yamlData, f)
                except ValueError:
                    return("Error on time conversion")
        finally:
            self.mutex.release()
        return ""


    def yaml_isActive(self, uid):
        self.mutex.acquire()
        try:
            uidStr = "UID" + str(uid)
            return self.yamlData[uidStr]["active"] == "true"
        finally:
            self.mutex.release()

    def yaml_info_get(self, uid):
        self.mutex.acquire()
        try:
            uidStr = "UID" + str(uid)
            active = self.yamlData[uidStr]["active"] == "true"
            startTime = self._convertToTime(self.yamlData[uidStr]["startTime"])
            endTime = self._convertToTime(self.yamlData[uidStr]["endTime"])
            return [active, startTime, endTime]
        finally:
            self.mutex.release()

    def _initYamlFile(self):
        print("creating default yaml file")
        fName = self._getYamlFileName()
        self.yamlData = dict(
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
            yaml.dump(self.yamlData, f)


    def _loadYamlFile(self):
        self.mutex.acquire()
        try:
            fName = self._getYamlFileName()
            if not os.path.isfile(fName) :
                self._initYamlFile()
            with open(fName) as f:
                # use safe_load instead load
                self.yamlData = yaml.safe_load(f)
        finally:
            self.mutex.release()


_GDATA = GLOBAL_DATA()


@app.route("/")
def index_html(errorString  = ''):
    global _GDATA
    print("index html")
    now = datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    yamlData = _GDATA.yaml_data_get()
    templateData = {
        'error_text' : errorString,
        'title' : 'HELLO!',
        'time': timeString,
        'uid0_active': yamlData["UID0"]["active"],
        'uid0_start' : yamlData["UID0"]["startTime"],
        'uid0_stop'  : yamlData["UID0"]["endTime"],
        'uid1_active': yamlData["UID1"]["active"],
        'uid1_start' : yamlData["UID1"]["startTime"],
        'uid1_stop'  : yamlData["UID1"]["endTime"]
    }
    return render_template('main_jinja2_template.html', **templateData)

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
    print(f"timepicker_report {UID} {active} {startTime} {endTime} ")
    errorText = _GDATA.updateConfigFile(uid = UID,active = active, start = startTime, end = endTime)
    return index_html(errorText)


class myThread (Thread):
    def __init__(self, threadID, name):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.PinActive = False
    
    def processUid(self, uid):
        [active, startTime, endTime] = _GDATA.yaml_info_get(uid)
        #if active and 

    def run(self):
        global _GDATA
        print ("Starting " + self.name)
        while(1):
            time.sleep(1)
            for uid in range(1):
                self.processUid(uid)
        print ("Exiting " + self.name)

if __name__ == "__main__":
    thread1 = myThread(1, "PinWorker")
    thread1.start()
    app.run(host='0.0.0.0', port=5000, debug=True)
