from flask import Flask
try:
    from sush_utils.sush_utils import system_uptime #import if this file is a lib
except:
    from sush_utils import system_uptime #import fallback if file runs locally


def start_simple_flask_not_returning():
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        uptime_hours = system_uptime.string_get()
        return 'Hello, World! Uptime: ' + uptime_hours

    #use_reloader = False is to prevent this file to be started multiple times, resulting in multiple threads
    #                and duplicated data structurs
    
    app.run(host='0.0.0.0', port=5000, debug=False,use_reloader=False)

if __name__ == "__main__":
    import logging
    logger = logging.getLogger('simple_flask')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('simple_flask.log')
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
    logger.info("starting flask now...")
    try:
        start_simple_flask_not_returning()
    except Exception as e:
        logger.error("Exception : " + str(e))
    
    logger.info("flask done - exit")