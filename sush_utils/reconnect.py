import os
from threading import Thread, Lock
import time
import logging
from sush_utils import sush_utils


def startReconnect(logger):
    threadReconnect = ThreadReconnect(1, "PinWorker", logger)
    threadReconnect.start()


class ThreadReconnect(Thread):
    def __init__(self, threadID, name, logger):
        Thread.__init__(self)
        self.log = logger
        self.threadID = threadID
        self.name = name
    

    def run(self):
        self.log.info('up and running')
        counter = 60
        while(True):
            try:
                time.sleep(60)
                if not self.pingable():
                    self.log.info('Going to reload')
                    os.system("sudo systemctl daemon-reload")
                    self.log.info('Going to restart')
                    time.sleep(10)
                    os.system("sudo systemctl restart dhcpcd")
                    self.log.info('restarted dhcpcd')
                    time.sleep(120)
                    if self.pingable():
                        self.log.info('connection reestablished')

                if counter == 60:
                    counter = 0
                    self.log.info("Heartbeat : " + sush_utils.getSystemUpTime_string())
                counter = counter +1
            except Exception as e:
                self.log.error("Exception : " + str(e))
                time.sleep(10)


    def pingable(self):
        hostname = "192.168.1.1"
        response = os.system("ping -c 1 " + hostname + " > /dev/null")

        #and then check the response...
        if response == 0:
            #self.log.debug('is up!')
            return True
        else:
            self.log.info('ping test failure, server is down!')
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
    startReconnect(logger)