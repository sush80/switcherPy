from flask import Flask, current_app


from sush_utils.sush_utils import system_uptime
from switcher2.shared_data import shared_data

HTML_NEWLINE = "<br>"

def start_simple_flask_not_returning():
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        uptime_hours = system_uptime.string_get()
        sharedData = current_app._get_current_object().config["_SHAREDDATA"]
        sharedData.load_from_file()
        [start, end, active] = sharedData.timer_get_as_string()
        html = "Uptime: " + uptime_hours  + HTML_NEWLINE + HTML_NEWLINE
        html = html + "Start : " + start + HTML_NEWLINE
        html = html + "End   : " + end + HTML_NEWLINE
        html = html + "Active: " + active + HTML_NEWLINE
        return html

    #use_reloader = False is to prevent this file to be started multiple times, resulting in multiple threads
    #                and duplicated data structurs
    
    sharedData = shared_data()

    # that is the ONLY ! Place where the flask app can access global data !
    app.config.update(_SHAREDDATA = sharedData)
    app.run(host='0.0.0.0', port=5000, debug=False,use_reloader=False)
