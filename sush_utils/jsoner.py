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
    dictionary = {'hello':'world'}
    my_jsoner = jsoner("__test.json")
    pprint.pprint(dictionary)
    assert not my_jsoner.has_new_data()
    my_jsoner.write(dictionary)
    assert my_jsoner.has_new_data()
    b = my_jsoner.read()
    assert not my_jsoner.has_new_data()
    pprint.pprint(b)
    b["hello"] = "newWorld"
    my_jsoner.write(b)
    assert my_jsoner.has_new_data()
    print("DONE ALL OK")

    
