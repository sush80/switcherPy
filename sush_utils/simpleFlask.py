from flask import Flask
from sush_utils.sush_utils import system_uptime



def start_simple_flask_not_returning():
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        uptime_hours = system_uptime.string_get()
        return 'Hello, World! Uptime: ' + uptime_hours

    #use_reloader = False is to prevent this file to be started multiple times, resulting in multiple threads
    #                and duplicated data structurs
    
    app.run(host='0.0.0.0', port=5000, debug=False,use_reloader=False)