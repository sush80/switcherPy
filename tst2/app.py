from flask import Flask, jsonify, render_template, request
import datetime
import yaml
import os.path

app = Flask(__name__)

yamlData = None

@app.route("/")
def index_html():
    global yamlData
    print("index html")
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    templateData = {
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
    now = datetime.datetime.now()
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
    print("timepicker_report")
    print(request.args)
    startTime = request.form.get('start')
    endTime = request.form.get('end')
    active = request.form.get('active')
    UID = request.form.get('UID')
    print(f"timepicker_report {UID} {active} {startTime} {endTime} ")
    _updateConfigFile(uid = UID,active = active, start = startTime, end = endTime)
    return index_html()



def _getYamlFileName():
    return 'data.yml'

def _updateConfigFile(uid, active="false", start="", end=""):
    global yamlData
    #with open(g_etYamlFileName(), 'w') as outfile:
    #    yaml.dump(data, outfile, default_flow_style=False)
    uidStr = "UID" + uid
    yamlData[uidStr]["active"] = active
    yamlData[uidStr]["startTime"] = start
    yamlData[uidStr]["endTime"] = end
    
    fName = _getYamlFileName()
    with open(fName, "w") as f:
        yaml.dump(yamlData, f)


def yaml_isActive(uid):
    global yamlData
    uidStr = "UID" + uid
    return yamlData[uidStr]["active"] == "true"


def _loadYamlFile():
    global yamlData
    fName = _getYamlFileName()
    if not os.path.isfile(fName) :
        print("creating default yaml file")
        yamlData = dict(
                UID0 = dict(
                    UID = '0',
                    active = 'false',
                    startTime = '00:0:00',
                    endTime = '00:0:00')
                ,
                UID1 = dict(
                    UID = '1',
                    active = 'false',
                    startTime = '00:0:00',
                    endTime = '00:0:00')
                )
        with open(fName, "w") as f:
            yaml.dump(yamlData, f)
    with open(fName) as f:
        # use safe_load instead load
        yamlData = yaml.safe_load(f)

if __name__ == "__main__":
    _loadYamlFile()
    app.run(host='0.0.0.0', port=5000, debug=True)
