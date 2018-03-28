from switcher.srv import startSwitcher
from sush_utils.simpleFlask import startSimpleFlask

if __name__ == "__main__":
    startSwitcher()
    startSimpleFlask()
"""     while(True):
        logger.info("Running reduced set of functions : " + mySushUtils.getSystemUpTime_string())
        time.sleep(60*60) """