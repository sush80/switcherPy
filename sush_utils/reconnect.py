import os
from threading import Thread, Lock
import time
import logging
try:
    from sush_utils.sush_utils import system_uptime #import if this file is a lib
except:
    from sush_utils import system_uptime #import fallback if file runs locally


def start_wifi_reconnect(logger):
    threadReconnect = ThreadWifiReconnect(1, "wifi_recoonnect", logger)
    threadReconnect.start()


class ThreadWifiReconnect(Thread):
    def __init__(self, threadID, name, logger):
        Thread.__init__(self)
        self.log = logger
        self.threadID = threadID
        self.name = name
    

    def run(self):
        self.log.info('up and running')
        while(True):
            try:
                time.sleep(60)

                if self.test_online():
                    continue
                
                self.log.info('Going to reload')
                os.system("sudo systemctl daemon-reload")
                self.log.info('Going to restart')
                time.sleep(30)
                os.system("sudo systemctl restart dhcpcd")
                self.log.info('restarted dhcpcd')
                time.sleep(120)
                if self.test_online():
                    self.log.info('connection reestablished')
                else:
                    self.log.info("could not reestablish connection")

            except Exception as e:
                self.log.error("Exception : " + str(e))
                time.sleep(60)

    def test_online(self, retries = 5, sleep_time = 60):
        for i in range(retries):
            if self.pingable():
                return True
            time.sleep(sleep_time)
        return False


    def pingable(self):
        hostname = "192.168.1.1"
        response = os.system("ping -c 1 " + hostname + " > /dev/null")

        #and then check the response...
        if response == 0:
            #self.log.debug('is up!')
            return True
        else:
            return False

    

if __name__ == "__main__":

    logger = logging.getLogger('reconnecterStandalone')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('reconnecterStandalone.log')
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
    start_wifi_reconnect(logger)