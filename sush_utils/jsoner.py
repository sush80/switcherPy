import json
import os

class jsoner():
    def __init__(self, filename, data_to_create_new_file = None):
        self.filename = filename
        if data_to_create_new_file:
            if not os.path.isfile(self.filename):
                self.write(data_to_create_new_file)
        self.last_modification = os.stat(self.filename)

    def write(self, data):
        with open(self.filename, 'w') as outfile:  
            json.dump(data, outfile)

    def read(self):
        with open(self.filename) as json_file:  
            data = json.load(json_file)
            return data

    def has_new_data(self):
        temp = os.stat(self.filename)
        if temp != self.last_modification:
            self.last_modification = temp
            return True
        return False




if __name__ == "__main__":
    import pprint
    dictio = {"timer_start": "06:00", "timer_end": "06:00", "timer_active": False }
    my_jsoner = jsoner("__test.json", dictio)
    pprint.pprint(dictio)
    assert not my_jsoner.has_new_data()
    my_jsoner.write(dictio)
    assert my_jsoner.has_new_data()
    b = my_jsoner.read()
    assert not my_jsoner.has_new_data()
    pprint.pprint(b)
    b["timer_end"] = "newWorld"
    my_jsoner.write(b)
    assert my_jsoner.has_new_data()
    c = my_jsoner.read()
    pprint.pprint(c)
    print("DONE ALL OK")

    
