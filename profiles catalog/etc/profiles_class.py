import json
import time
from datetime import datetime
from etc.generic_service import *

"""
Updates: Changeing room to patient.
"""

class NewProfile():
    def __init__(self,platform_ID,platform_name,location, Patients,lastUpdate):
        self.platform_ID=platform_ID
        self.platform_name=platform_name
        self.location=location
        self.lastUpdate=lastUpdate
        self.warning=True
        self.Patient_cnt=0
        self.Patients=Patients
        
    def jsonify(self):
        profile={"platform_ID":self.platform_ID,
                 'platform_name':self.platform_name,
                 'warning':self.warning,
                 'Patient_cnt':self.Patient_cnt,
                 'location':self.location,'Patients':self.Patients,'creation_date':self.lastUpdate}
        return profile

class NewPatient():
    def __init__(self,Patient_ID,Patient_name,def_content):
        Patient_info={}
        Patient_info['Patient_ID']=Patient_ID
        Patient_info['connection_flag']=False
        Patient_info['preferences']=self.load_def(def_content,Patient_name)
        Patient_info['preferences']['Patient_name']=Patient_name
        timestamp=time.time()
        Patient_info['connection_timestamp']=timestamp
        self.Patient_info=Patient_info
    
    def load_def(self,json_content,Patient_name):
        try:
            info=json_content[Patient_name.lower()]
        except:
            info=json_content["default"].copy()
        return info 
        
    def jsonify(self):
        return self.Patient_info

class ProfilesCatalog(Generic_Service):
    def __init__(self,conf_filename, db_filename,def_file="data/default_profile.json"):
        Generic_Service.__init__(self,conf_filename,db_filename)
        self.default_profile=json.load(open(def_file,"r"))

    def retrieveProfileInfo(self,platform_ID):
        notFound=1
        for profile in self.db_content['profiles']:
            if profile['platform_ID']==platform_ID:
                notFound=0
                return profile
        if notFound==1:
            return False

    def retrieveProfileParameter(self,platform_ID,parameter):
        profile=self.retrieveProfileInfo(platform_ID)
        try:
            result= profile[parameter]
        except:
            result=False
        return result

    def insertProfile(self,platform_ID,platform_name):
        notExisting=1
        now=datetime.now()
        timestamp=now.strftime("%d/%m/%Y %H:%M")
        profile=self.retrieveProfileInfo(platform_ID)
        if profile is False:
            location=None
            Patients=[]
            createdProfile=NewProfile(platform_ID,platform_name,location,Patients,timestamp).jsonify()
            self.db_content['profiles'].append(createdProfile)
            self.db_content['last_creation']=timestamp
            return True
        else:
            return False

    def insertPatient(self,platform_ID,Patient_name):
        profile=self.retrieveProfileInfo(platform_ID)
        PatientNotFound=1
        if profile is not False:
            Patient_cnt=self.retrieveProfileParameter(platform_ID,'Patient_cnt')+1
            Patient_ID="Patient_"+str(Patient_cnt)
            new_Patient=NewPatient(Patient_ID,Patient_name,self.default_profile)
            for Patient in profile['Patients']:
                if Patient['preferences']['Patient_name']==Patient_name:
                    rooPatientNotFound=0
                    break
            if PatientNotFound==1:
                profile['Patients'].append(new_Patient.jsonify())
                self.setParameter(platform_ID,'Patient_cnt',Patient_cnt)
                return new_Patient
            else:
                return False
        else:
            return False

    def associatePatient(self,platform_ID,request_timestamp):
        platform=self.retrieveProfileInfo(platform_ID)
        notFound=1
        if platform is not False:
            for Patient in platform['Patients']:
                if Patient['connection_flag'] is False and (request_timestamp-Patient['connection_timestamp'])<300:
                    Patient['connection_flag']=True
                    notFound=0
                    return Patient
            if notFound==1:
                return False
        else:
            return False


    def removeProfile(self,platform_ID):
        profile=self.retrieveProfileInfo(platform_ID)
        if profile is not False:
            self.db_content["profiles"].remove(profile)
            return True
        else:
            return False
        
    def removePatient(self,platform_ID,Patient_ID):
        profile=self.retrieveProfileInfo(platform_ID)
        if profile is not False:
            Patient=self.retrievePatientInfo(profile['Patients'],Patient_ID)
            if Patient is not False:
                profile['Patients'].remove(Patient)
                return True
            else:
                return False
        else:
            return False
        
        
    def setParameter(self, platform_ID, parameter, parameter_value):
        profile=self.retrieveProfileInfo(platform_ID)
        if profile is not False:
            profile[parameter]=parameter_value
            return True
        else:
            return False
        
    def retrievePatientInfo(self,Patients,Patient_ID):
        notFound=1
        for Patient in Patients:
            if Patient['Patient_ID']==Patient_ID:
                notFound=0
                return Patient
        if notFound==1:
            return False

    def retrievePatientList(self, Patients):
        output=[]
        for Patient in Patients:
            output.append(Patient['Patient_ID'])
        return output
        
    def PatientParameter(self,platform_ID,Patient_ID,body):
        profile=self.retrieveProfileInfo(platform_ID)
        if profile is not False:
            Patients=profile['Patients']
            Patient=self.retrievePatientInfo(Patients,Patient_ID)
            if Patient is not False:
                for key in body.keys():
                    try:
                        for subkey in body[key]:
                            Patient['preferences'][key][subkey]=body[key][subkey]
                        return True
                    except:
                        Patient['preferences'][key]=body[key]
                        return True
            else:
                return False
        else:
            return False
        
    def save(self):
        with open(self.db_filename,'w') as file:
            json.dump(self.db_content,file, indent=4)









