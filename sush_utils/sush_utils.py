from datetime import datetime, timedelta
import os
import time
import subprocess



class system_uptime(object):

    @staticmethod
    def seconds_get():
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                return uptime_seconds
        except:
            return 0

    @staticmethod
    def hours_get():
        uptime_seconds = system_uptime.seconds_get()
        return uptime_seconds/(60*60)

    @staticmethod
    def string_get():
        try:
            uptime_seconds = system_uptime.seconds_get()
            uptime_string = str(timedelta(seconds = uptime_seconds))
            return uptime_string
        except:
            return "<no uptime>"

class sush_utils(object):

    def __init__(self, logger):
        self.logger = logger

    '''
        Blocks until systemd-timesyncd has updated local time with a proper one
        from some NTP Server.
    '''
    def time_synchronisation_barrier(self, initial_delay_s = 30, poll_intervall_s = 60*10):
        time.sleep(initial_delay_s)
        self.logger.info("time_synchronisation_barrier : starting")
        while(True):
            try:
                ret = subprocess.check_output(['systemctl', 'status', 'systemd-timesyncd'])
                if "Synchronized to time server" in str(ret):
                    self.logger.info("Time synced with NTP Server")
                    return
                self.logger.info("time_synchronisation_barrier : No connection to time server, will retry")
                time.sleep(poll_intervall_s)
            except FileNotFoundError:
                self.logger.warn("time_synchronisation_barrier : Most likely running on non Raspbery -> continue")
                return