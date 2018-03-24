from datetime import datetime, timedelta
import os
import time
import subprocess

class sush_utils(object):

    def __init__(self, logger):
        self.logger = logger

    def getSystemUpTime_seconds(self):
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                return uptime_seconds
        except:
            return 0

    @staticmethod
    def getSystemUpTime_hours():
        uptime_seconds = sush_utils.getSystemUpTime_seconds()
        return uptime_seconds/(60*60)

    @staticmethod
    def getSystemUpTime_string():
        try:
            uptime_seconds = sush_utils.getSystemUpTime_seconds()
            uptime_string = str(timedelta(seconds = uptime_seconds))
            return uptime_string
        except:
            return "<no uptime>"

    '''
        Blocks until systemd-timesyncd has updated local time with a proper one
        from some NTP Server.
    '''
    def time_synchronisation_barrier(self, initial_delay_s = 10, poll_intervall_s = 60*10):
        time.sleep(initial_delay_s)
        while(True):
            try:
                ret = subprocess.check_output(['systemctl', 'status', 'systemd-timesyncd'])
                if "Synchronized to time server" in ret:
                    self.logger.info("Time synced with NTP Server")
                    return
                self.logger.info("No connection to time server, will retry")
                time.sleep(poll_intervall_s)
            except FileNotFoundError:
                self.logger.warn("Most likely running on non Raspbery -> continue")
                return