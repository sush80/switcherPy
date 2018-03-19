from flask import Flask
import time
from datetime import datetime, timedelta
import time
import yaml
import os.path
from threading import Thread, Lock
import copy
import os,sys
import logging
import sys
sys.path.insert(0, "../sush_utils")
try:
    from sush_utils import getSystemUpTime_hours, getSystemUpTime_seconds, getSystemUpTime_string
    from reconnect import startReconnect
except ImportError:
    print('No Import')



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


app = Flask(__name__)

@app.route('/')
def hello_world():
    uptime_hours = getSystemUpTime_string()
    return 'Hello, World! uptime_hours: ' + uptime_hours


class Thread_Uptime (Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        logger.debug ("Starting Thread_Uptime" )
        while(1):
            uptime_hours = getSystemUpTime_string()
            logger.info("ThreadUptime - uptime_hours : " + uptime_hours)
            time.sleep(60*60)
        logger.debug ("Exiting " + self.name)


if __name__ == "__main__":
    #start threads
    while(True):
        now = datetime.now()
        if now.year > 2017:
            break
        logger.warning("local clock not up to date, postponing start of server:" + str(now))
        time.sleep(10)


    THREAD_UPTIME = Thread_Uptime()
    THREAD_UPTIME.start()
    
    logger.info("Will start flask now")
    
    #use_reloader = False is to prevent this file to be started multiple times, resulting in multiple threads
    #                     and duplicated data structurs
    app.run(host='0.0.0.0', port=5000, debug=True,use_reloader=False)