from flask import Flask, current_app, render_template, request
import logging
import time


from sush_utils.sush_utils import system_uptime, DS18B20_temperature_get
from switcher3.shared_data import shared_data

HTML_NEWLINE = "<br>"

def start_simple_flask_not_returning(logger):
    app = Flask(__name__)

    @app.route("/index.html", methods=['GET', 'POST'])
    def index_html():
        return ROOT()

    @app.route('/')
    def ROOT():
        errorString = ""
        upTimeString = system_uptime.string_get()
        sharedData = current_app._get_current_object().config["_SHAREDDATA"]
        logger = current_app._get_current_object().config["_LOGGER"]
        logger.debug("starting reading temperature")
        temperature = DS18B20_temperature_get(devicename = '/sys/bus/w1/devices/28-0317019e9eff/w1_slave')
        logger.debug("Done reading temperature : " + temperature)

        if request.form.get('action') == "setAlarmTimes":
            startTime = request.form.get('start')
            stopTime = request.form.get('stop')
            active = str("true" == request.form.get('active')).lower()
            logger.debug("setAlarmTimes: "  + " " + (active) + " " + (startTime) + " " + (stopTime))
            try:
                sharedData.store( startTime, stopTime, active)
            except:
                errorString = "could not write data to cfg file "
                logger.error(errorString)

            #errorString = _GDATA.updateConfigFile(uid = UID,active = active, start = startTime, end = stopTime)
        else:
            logger.debug("no action")

        [start, end, active] = sharedData.load(returnType = "string")

        try:
            templateData = {
                'error_text' : errorString,
                'title' : 'Switcher!',
                'time': time.strftime("%Y-%m-%d %H:%M"),
                'uid0_active': active,
                'uid0_start' : start,
                'uid0_stop'  : end,
                'current_status_active' : "FIXME_curent_status",
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


        html = "Uptime: " + upTimeString  + HTML_NEWLINE + HTML_NEWLINE
        html = html + "Start : " + start + HTML_NEWLINE
        html = html + "End   : " + end + HTML_NEWLINE
        html = html + "Active: " + active + HTML_NEWLINE + HTML_NEWLINE
        html = html + '<a href ="timepicker.html"> Change Timer </a>' + HTML_NEWLINE
        return html

    @app.route("/timepicker.html", methods=['GET'])
    def timepicker():

        templateData = {
            'start' : request.args.get('start'),
            'stop' : request.args.get('stop')
        }
        return render_template('timepicker.html', **templateData)



    #use_reloader = False is to prevent this file to be started multiple times, resulting in multiple threads
    #                and duplicated data structurs
    
    sharedData = shared_data()

    # that is the ONLY ! Place where the flask app can access global data !
    app.config.update(_SHAREDDATA = sharedData)

    # that is the ONLY ! Place where the flask app can access global data !
    app.config.update(_SHAREDDATA = sharedData)
    app.config.update(_LOGGER = logger)

    app.run(host='0.0.0.0', port=5000, debug=False,use_reloader=False)
