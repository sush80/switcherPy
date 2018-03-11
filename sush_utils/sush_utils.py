from datetime import datetime, timedelta


def getSystemUpTime_seconds():
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            return uptime_seconds
    except:
        return 0

def getSystemUpTime_hours():
    uptime_seconds = getSystemUpTime_seconds()
    return uptime_seconds/(60*60)

def getSystemUpTime_string():
    try:
        uptime_seconds = getSystemUpTime_seconds()
        uptime_string = str(timedelta(seconds = uptime_seconds))
        return uptime_string
    except:
        return "<no uptime>"

