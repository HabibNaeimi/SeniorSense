import json, time
from datetime import datetime

class PatientObj():
    def __init__(self,patient_ID,MRT,devices,timestamp):
        self.patient_ID=patient_ID
        self.timestamp=timestamp
        self.MRT=MRT
        self.devs=devices
        
    def jsonify(self):
        patient={'patient_ID':self.patient_ID,'devices':self.devs,'last_update':self.timestamp}
        return patient

class PatientsCatalog():
    def __init__(self,myPatients):
        self.myPatients=myPatients
        self.now=datetime.now()
        self.timestamp=self.now.strftime("%d/%m/%Y %H:%M")

    def findPat(self,patient_ID):
        notFound=1
        for i in range(len(self.myPatients)): 
            if self.myPatients[i]['patient_ID']==patient_ID:
                notFound=0
                return i
        if notFound==1:
            return False

    def setParameter(self, patient_ID, parameter, parameter_value):
        if parameter != "patient_ID":
            i=self.findPos(patient_ID)
            if i is not False:
                self.myPatients[i][parameter]=parameter_value
                return True
            else:
                return False
        else:
            return False

    def addPatient(self,patient_ID,patient):
        output=True
        i=self.findPos(patient_ID)
        if i is not False:
            self.removePatient(patient_ID)
            output=False
        self.myPatients.append(patient)
        return output

    def removePatient(self,patient_ID):
        i=self.findPos(patient_ID)
        if i is not False:
            self.myPatients.pop(i) 
            return True
        else:
            return i


   

