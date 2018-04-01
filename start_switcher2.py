
from switcher2.srv import start_pinworker, start_flask
from sush_utils.reconnect import start_wifi_reconnect, system_uptime
from sush_utils.sush_utils import time_synchronisation_barrier

import logging
import time


if __name__ == "__main__":
    logger = logging.getLogger('switcher2')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('switcher2.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh) # FileHandler 
    logger.addHandler(ch)
    #fixme_flask app = Flask(__name__)

    logger.info("__________________________")
    
    time_synchronisation_barrier(logger)

    start_wifi_reconnect(logger)
    start_pinworker(logger)
    start_flask()

    while(True):
        logger.info("Running reduced set of functions : " + system_uptime.string_get())
        time.sleep(60*60) 