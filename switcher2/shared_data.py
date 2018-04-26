from datetime import datetime, timedelta
import time
import os.path
from threading import Thread, Lock
import copy

from sush_utils.jsoner import jsoner

class shared_data(object):

    class __SharedData(object):
        def __init__(self):
            self._lock = Lock()
            self._data_dict = {"timer_start": "06:00", "timer_end": "06:00", "timer_active": False }
            self._jsoner = jsoner("switcher.cfg", self._data_dict)
            self.load_from_file(force = True)

        def load_from_file(self, force = False):
            if self._jsoner.has_new_data() or force:
                self._data_dict = self._jsoner.read()
                self._timer_start = self._time_from_string(self._data_dict["timer_start"])
                self._timer_end = self._time_from_string(self._data_dict["timer_end"])
                self._timer_active = self._data_dict["timer_active"]
                assert type(self._timer_active) == type(True)

       
        # Format HH:MM
        def _time_from_string(self, timer):
            return datetime.strptime(timer, '%H:%M').time()

        # Format HH:MM
        def _time_to_string(self, timer):
            return timer.strftime("%H:%M")
        
        def timer_set(self, start, end):
            with self._lock:
                if isinstance(start, "") and isinstance(end, ""):
                    start = self._time_from_string(start)
                    end = self._time_from_string(end)
                self._timer_start = start
                self._timer_end = end
                #FIXME STORE TO FILE
            
        def timer_get(self):
            with self._lock:
                start = copy.deepcopy(self._timer_start)
                end = copy.deepcopy(self._timer_end)
                active = copy.deepcopy(self._timer_active)
                return [start, end, active]
            
        def timer_get_as_string(self):
            [start, end, active] = self.timer_get()
            return [copy.deepcopy(self._time_to_string(start)), copy.deepcopy(self._time_to_string(end)), copy.deepcopy(str(active))]

    __instance = None
    
    def __init__(self):
        if not shared_data.__instance:
            shared_data.__instance = shared_data.__SharedData()
    def __getattr__(self, name):
        return getattr(self.__instance, name)

