import json
from datetime import datetime
import time

#it could be useless if a specific structure is not imposed.
class Device():
    def __init__(self,deviceID,endpoints,info):
        self._deviceID=deviceID
        self.endpoints=endpoints
        self.info=info
        self.timestamp=time.time()
        self.date=datetime.now().strftime("%d/%m/%Y %H:%M")
    
    def jsonify(self):
        device={'deviceID':self._deviceID,'endpoints':self.endpoints,'resources':self.info,'timestamp':self.timestamp,'date':self.date}
        return device

class DevicesCatalog():
    def __init__(self,devices_list):
        self.devs=devices_list

    def insertValue(self,dev_ID,info):
        if not any(dev['deviceID']==dev_ID for dev in self.devs):
            return self.addDevice(dev_ID,info)
        else:
            return self.updateDevice(dev_ID,info)
    
    def updateDevice(self,dev_ID,info):
        for device in self.devs:
            if device['deviceID']==dev_ID:
                timestamp=time.time()
                date=datetime.now().strftime("%d/%m/%Y %H:%M")
                device['timestamp']=timestamp
                device['resources']=info['e']
                device['date']=date
                print("Device {} updated.\n".format(dev_ID))
                return True


    def addDevice(self,dev_ID,dev_info):
        try:
            device=Device(dev_ID,dev_info['endpoints'],dev_info['e']).jsonify()
            self.devs.append(device)
            print("New device {} added.\n".format(dev_ID))
            return True
        except Exception as e:
            print(e)
            print("New device {} can't be added.\n".format(dev_ID))
            return False
        
    def removeInactive(self,timeInactive):
        removed_devs=[]
        for device in self.devs:
            dev_ID=device['deviceID']
            if time.time() - device['timestamp']>timeInactive:
                self.devs.remove(device)
                #self.devices['last_update']=self.actualTime
                print(f'Device {dev_ID} removed')
                removed_devs.append(dev_ID)
        return removed_devs

    def findPos(self,dev_ID):
        notFound=1
        for i in range(len(self.devs)):
            if self.devs[i]['deviceID']==dev_ID:
                notFound=0
                return i
        if notFound==1:
            return False
        
    def removeDevice(self,dev_ID):
        i=self.findPos(dev_ID)
        if i is not False:
            self.devs.pop(i) 
            return True
        else:
            return i

    
