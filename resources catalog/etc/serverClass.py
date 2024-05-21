import json, time
from datetime import datetime
from etc.generic_service import *
from etc.devices_catalog import DevicesCatalog
from etc.patients_catalog import PatientsCatalog

class NewPlatform():
    def __init__(self,platform_ID,patients,last_update):
        self.platform_ID=platform_ID
        self.patients=patients
        self.lastUpdate=last_update

    def jsonify(self):
        platform={'platform_ID':self.platform_ID,'patients':self.patients,'creation_date':self.lastUpdate}
        return platform
    
class ResourceService(Generic_Service):
    def __init__(self,conf_fname,db_fname):
        Generic_Service.__init__(self,conf_fname,db_fname)
        self.delta=self.conf_content.get('delta')
                
    def retrievePlatformsList(self):
        platformsList=[]
        for platform in self.db_content['platforms_list']:
            platformsList.append(platform['platform_ID'])
        return platformsList
    
    def retrievePlatform(self,platform_ID):
        notFound=1
        for platform in self.db_content['platforms_list']:
            if platform['platform_ID']==platform_ID:
                notFound=0
                return platform
        if notFound==1:
            return False

    def retrievePatientInfo(self,platform_ID,patient_ID):
        notFound=1
        platform=self.retrievePlatform(platform_ID)
        if platform is not False:
            for patient in platform['patients']:
                if patient['patient_ID']==patient_ID:
                    notFound=0
                    return patient
                if notFound==1:
                    return False
        else:
            return False

    def retrieveDeviceInfo(self,platform_ID,patient_ID,dev_ID):
         notFound=1
         patient=self.retrievePatientInfo(platform_ID,patient_ID)
         for device in patient['devices']:
             if device['deviceID']==dev_ID:
                 notFound=0
                 return device
         if notFound==1:
             return False

    def retrieveParameterInfo(self,platform_ID,patient_ID,dev_ID,parameter_name):
        notFound=1
        device=self.retrieveDeviceInfo(platform_ID,patient_ID,dev_ID)
        for parameter in device['resources']:
            if parameter['n']==parameter_name:
                notFound=0
                return parameter
        if notFound==1:
            return False

    def findParameter(self,platform_ID,patient_ID,parameter_name):
        notFound=1
        patient=self.retrievePatientInfo(platform_ID,patient_ID)
        try:
            p=patient[parameter_name]
            parameter={"parameter":parameter_name,"value":p}
            return parameter
        except:
            for device in patient['devices']:
                parameter=self.retrieveParameterInfo(platform_ID,patient_ID,device['deviceID'],parameter_name)
                if parameter is not False:
                    notFound=0
                    new_parameter=parameter.copy()
                    new_parameter['deviceID']=device['deviceID']
                    return new_parameter
            if notFound==1:
                return False

    def insertPlatform(self,platform_ID,patients):
        notExisting=1
        now=datetime.now()
        timestamp=now.strftime("%d/%m/%Y %H:%M")
        platform=self.retrievePlatform(platform_ID)
        if platform is False:
            createdPlatform=NewPlatform(platform_ID,patients,timestamp).jsonify()
            self.db_content['platforms_list'].append(createdPlatform)
            return True
        else:
            return False

    def addPatient(self,platform_ID,patient_ID,patient):
        platform=self.retrievePlatform(platform_ID)
        existingFlag=False
        self.patientsCatalog=PatientsCatalog(platform['patients'])
        existingFlag=self.patiensCatalog.addPatient(patient_ID,patient)
        if existingFlag:
            output="Platform '{}' - Patient '{}' has been added to Server".format(platform_ID, patient_ID)
        else:
            output="Platform '{}' - Patient '{}' already exists. Resetted...".format(platform_ID,patient_ID)

    def insertDevice(self,platform_ID,patient_ID,msg):
        print(platform_ID+"->"+patient_ID)
        patient=self.retrievePatientInfo(platform_ID,patient_ID)
        if patient is not False:
            catalog=DevicesCatalog(patient['devices'])
            dev_ID=msg['bn']
            result=catalog.insertValue(dev_ID,msg)
            if result is False:
                print("Not saving..")
                return False
            else:
                return True
        else:
            return False
        
    def removePlatform(self,platform_ID):
        notFound=True
        for i in range(len(self.db_content['platforms_list'])):
            if self.db_content['platforms_list'][i]['platform_ID']==platform_ID:
                self.db_content['platforms_list'].pop(i)
                notFound=False
                return True
        if notFound:
            return False

    def removePatient(self,platform_ID,patient_ID):
        platform=self.retrievePlatform(platform_ID)
        if platform is not False:
            patientsCatalog=PatientsCatalog(platform['patients'])
            result=patientsCatalog.removePatient(patient_ID)
            return result
        else:
            return False

    def removeDevice(self,platform_ID,patient_ID,dev_ID):
        patient=self.retrievePatientInfo(platform_ID,patient_ID)
        if patient is not False:
            devicesCatalog=DevicesCatalog(patient['devices'])
            result=devicesCatalog.removeDevice(dev_ID)
            return result
        else:
            return False

    def removeInactive(self,inactiveTime):
        for platform in self.db_content['platforms_list']:
            for patient in platform['patients']:
                devs=patient['devices']
                devicesCatalog=DevicesCatalog(devs)
            return devicesCatalog.removeInactive(inactiveTime)

    def dateUpdate(self,element):
        now=datetime.now()
        new_date=now.strftime("%d/%m/%Y/%H/%M")
        element['last_update']=new_date

    def save(self):
        with open(self.db_fname,'w') as file:
            json.dump(self.db_content,file, indent=4)
