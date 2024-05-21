import json
from datetime import datetime

class devsList():
    def __init__(self,filename):
        fileContent=json.load(open(filename))
        self.fileContent=fileContent
        self.devsList=[]
        for dev in self.fileContent['devs']:
            self.devsList.append(dev(dev.get('sensorID'),dev.get('end_points'),dev.get('parameters'),dev.get('timestamp')).jsonify())
    def show(self):
        for dev in self.devsList:
            print(dev)


class dev():
    def __init__(self,sensorID,endPoints,parameters,timestamp):
        self.sensorID=sensorID
        self.endPoints=endPoints
        self.parameters=parameters
        self.timestamp=timestamp
    
    def jsonify(self):
        dev={'sensorID':self.sensorID,'end_points':self.endPoints,'parameters':self.parameters,'timestamp':self.timestamp}
        return dev
