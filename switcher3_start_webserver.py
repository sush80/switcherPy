
from switcher3.flasker import start_simple_flask_not_returning
from sush_utils.sush_utils import time_synchronisation_barrier

import logging
import time


if __name__ == "__main__":
    import logging
    logger = logging.getLogger('flask')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('flask.log')
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


    time_synchronisation_barrier(logger) # to not read wrong cfg fiel modification time

    logger.info("starting flask now...")
    try:
        start_simple_flask_not_returning(logger)
    except Exception as e:
        logger.error("Exception : " + str(e))
    
    logger.info("flask done - exit")