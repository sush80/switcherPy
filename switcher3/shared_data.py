from datetime import datetime, timedelta
import time
import os.path
from threading import Thread, Lock
import copy

try:
    from sush_utils.jsoner import jsoner
    CFG_FILE = "switcher3/switcher.cfg"
except:
    # fallback for unit testing
    import sys
    sys.path.insert(0, "../sush_utils")
    from jsoner import jsoner
    CFG_FILE = "switcher.cfg"


class shared_data(object):

    class __SharedData(object):
        def __init__(self):
            self._lock = Lock()
            self._data_dict = {"timer_start": "06:00", "timer_end": "06:00", "timer_active": "false" }
            self._jsoner = jsoner(CFG_FILE, self._data_dict)
            self.load(force = True)

        def has_new_data(self):
            return self._jsoner.has_new_data()

        def load(self, force = False, returnType = "native"):
            '''
            returnType "native"
                returns hh:mm hh:mm bool
            returnType "string":
                returns e.g. "06:00", "06:00", "false" 
                Note that false and true are lowercase
            '''
            assert returnType == "native" or returnType == "string"
            new_data = self._jsoner.has_new_data()
            if new_data or force:
                _data_dict = self._jsoner.read()
                self._timer_start = self._time_from_string(_data_dict["timer_start"])
                self._timer_end = self._time_from_string(_data_dict["timer_end"])
                self._timer_active_bool = self._bool_from_string(_data_dict["timer_active"])
                assert type(self._timer_active_bool) == type(True)
            start = copy.deepcopy(self._timer_start)
            end = copy.deepcopy(self._timer_end)
            active = copy.deepcopy(self._timer_active_bool)
            if returnType == "string":
                start = self._time_to_string(start)
                end   = self._time_to_string(end)
                active = self._bool_to_string(active)
            return [start, end, active]

        def store(self, startString, endString, activeString):
            assert type(activeString) == type("aString")
            assert type(startString) == type("aString")
            assert type(endString) == type("aString")
            assert activeString == "true" or activeString == "false"
            _start = self._time_from_string(startString) # test if valid format
            _end = self._time_from_string(endString) # test if valid format
            #update data only when all conversions passed
            self._timer_start = _start
            self._timer_end = _end
            self._timer_active_bool = self._bool_from_string(activeString)
            self._jsoner.write({"timer_start": startString, "timer_end": endString, "timer_active": activeString })


        # Format HH:MM
        def _time_from_string(self, timer):
            return datetime.strptime(timer, '%H:%M').time()

        # Format HH:MM
        def _time_to_string(self, timer):
            return timer.strftime("%H:%M")

        def _bool_to_string(self, value):
            '''
                True  -> "true"
                False -> "false"
                None  -> "false"
            '''
            assert value == True or value == False or value == None
            return str(value == True).lower()

        def _bool_from_string(self,value):
            assert value == "true" or value == "false"
            return value == "true"
        
            

    __instance = None
    
    def __init__(self):
        if not shared_data.__instance:
            shared_data.__instance = shared_data.__SharedData()
    def __getattr__(self, name):
        return getattr(self.__instance, name)



if __name__ == "__main__":
    import pprint
    sharedData1 = shared_data()
    sharedData1.load(True)
    sharedData1.store("06:01", "06:02", "true")
    [start, end, active] = sharedData1.load(returnType = "string")
    print( " " + " " + start + " " + end + " " + active) 
    assert type(start) == type("aString")
    assert type(end) == type("aString")
    assert type(active) == type("aString")
    [start, end, active] = sharedData1.load()
    assert type(start) != type("aString")
    assert type(end) != type("aString")
    assert type(active) == type(True)

    sharedData1.store("06:05", "06:07", "false")
    [start, end, active] = sharedData1.load(returnType = "string")
    assert start == "06:05"
    assert end == "06:07"
    assert active == "false"
    print("DONE ALL OK")
