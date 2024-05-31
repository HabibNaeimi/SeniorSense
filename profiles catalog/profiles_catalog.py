import cherrypy
import json
import requests
import time
import sys
from etc.profiles_class import ProfilesCatalog

"""
Updates: Changeing room to patient.
"""

class catalogREST():
    exposed=True
    def __init__(self,conf_filename,db_filename):
        self.catalog=ProfilesCatalog(conf_filename,db_filename)
        self.service=self.catalog.registerRequest()
        
    def GET(self,*uri):
        uriLen=len(uri)
        output=False
        if uriLen!=0:
            profile= self.catalog.retrieveProfileInfo(uri[0])
            if profile is not False:
                if uriLen>1:
                    profileInfo= self.catalog.retrieveProfileParameter(uri[0],uri[1])
                    output=profileInfo
                    if uriLen>2:
                        if str(uri[2])=='patients_list':
                            PatientInfo=self.catalog.retrievePatientList(profileInfo)
                        else:
                            PatientInfo=self.catalog.retrievePatientInfo(profileInfo,uri[2])
                        if uriLen>3:
                            try:
                                output=PatientInfo[uri[3]]
                                if uriLen>4:
                                    try:
                                        output=PatientInfo["preferences"][uri[4]]
                                    except Exception as e:
                                        print(e)
                                        output=False
                            except:
                                output=False
                        else:
                            output=PatientInfo

                else:
                    output=profile

            if not output:
                raise cherrypy.HTTPError(404,"Information Not found")

        else:
            output=self.catalog.conf_content['description']

        return json.dumps(output) 

    def PUT(self, *uri):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        command=str(uri[0])
        saveFlag=False
        msg={"msg":None}
        if command=='insertProfile':
            try:
                platform_ID=json_body['platform_ID']
                platform_name=json_body['platform_ID']
            except:
                raise cherrypy.HTTPError("400 Bad Request! You need to specify parameters")
            newProfile=self.catalog.insertProfile(platform_ID,platform_name)
            if newProfile:
                output="Profile '{}' has been added to Profiles Database".format(platform_ID)
                msg['msg']=output
                saveFlag=True
            else:
                output="'{}' already exists!".format(platform_ID)
                raise cherrypy.HTTPError("409 Resource already exists!")
        #from bot
        elif command=='insertPatient':
            try:
                platform_ID=uri[1]
                Patient_name=json_body['Patient_name']
            except:
                raise cherrypy.HTTPError("400 Bad Request! You need to specify parameters")

            newPatient=self.catalog.insertPatient(platform_ID,Patient_name)
            if newPatient is not False:
                output="Patient '{}' has been added to platform '{}'".format(Patient_name,platform_ID)
                clients_service=self.catalog.retrieveService('clients_catalog')
                json_msg={"platformID":platform_ID,"PatientID":newPatient.Patient_info['Patient_ID']}
                thingspeak_association=requests.put(clients_service['url']+"/newPatient",json=json_msg)
                if thingspeak_association.status_code==200:
                    output=output+". "+thingspeak_association.json()['msg']
                    msg['msg']=output
                    saveFlag=True
                else:
                    self.catalog.removePatient(platform_ID,Patient_ID)
                    return thingspeak_association
            else:
                output="Patient '{}' cannot be added to platform '{}'".format(Patient_name,platform_ID)
                raise cherrypy.HTTPError("400 Platform not found")
                
        #from physical platform        
        elif command=='associatePatient':
            try:
                platform_ID=uri[1]
                timestamp=json_body['timestamp']
            except:
                raise cherrypy.HTTPError("400 Bad Request! You need to specify parameters")
            associatedPatient=self.catalog.associatePatient(platform_ID,timestamp)
            if associatedPatient is not False:
                output="Patient '{}' has been associated in platform '{}'".format(associatedPatient['preferences']['Patient_name'],platform_ID)
                msg['msg']={"Patient_ID": associatedPatient['Patient_ID'], "Patient_name": associatedPatient['preferences']['Patient_name'],"connection_timestamp":associatedPatient['connection_timestamp']}
                saveFlag=True
            else:
                output="Association failed in platform '{}' or already performed.".format(platform_ID)
                raise cherrypy.HTTPError("409 "+output)

        else:
            raise cherrypy.HTTPError("501 No operation!")
        
        if saveFlag:
            self.catalog.save()
        print(output)
        return json.dumps(msg)
		
    def POST(self, *uri):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        command=str(uri[0])
        if command=='setParameter':
            try:
                platform_ID=uri[1]
                parameter=json_body['parameter']
                parameter_value=json_body['parameter_value']
            except:
                raise cherrypy.HTTPError("400 Bad Request! You need to specify parameters")
            newSetting=self.catalog.setParameter(platform_ID,parameter,parameter_value)
            if newSetting:
                output="Platform '{}': {} is now {}".format(platform_ID, parameter,parameter_value)
                self.catalog.save()
            else:
                output="Platform '{}': Can't change {} ".format(platform_ID, parameter)
                raise cherrypy.HTTPError(404, "No resource available!")
            print(output)
            return json.dumps({"msg":output})

        elif command=='setPatientParameter':
            try:
                platform_ID=uri[1]
                Patient_ID=uri[2]
            except:
                raise cherrypy.HTTPError("400 Bad Request! You need to specify parameters")

            newSetting=self.catalog.setPatientParameter(platform_ID,Patient_ID,json_body)
            if newSetting:
                output="Platform '{}' - Patient '{}': parameter updated".format(platform_ID,Patient_ID)
                self.catalog.save()
            else:
                output="Platform '{}' Patient '{}': Can't change parameter".format(platform_ID, Patient_ID)
                raise cherrypy.HTTPError(404, "No resource available!")
            print(output)
            return json.dumps({"msg":output})

        else:
            raise cherrypy.HTTPError(501, "No operation!")

    def DELETE(self,*uri):
        command=str(uri[0])
        try:
            clients_service=self.catalog.retrieveService('clients_catalog')
        except:
            raise cherrypy.HTTPError("503 Can't perform the request now...")
        if command=='removeProfile':
            try:
                username=uri[1]
                platform_ID=uri[2]
            except:
                raise cherrypy.HTTPError("400 Bad Request! You need to specify parameters")
            r_client=requests.delete(clients_service['url']+"/removePlatform/"+username+"/"+platform_ID)
            if r_client.status_code==200:
                removedProfile=self.catalog.removeProfile(platform_ID)
                if removedProfile:
                    output="Profile '{}' removed".format(platform_ID)
                    resource_service=self.catalog.retrieveService('resource_catalog')
                    try:
                        requests.delete(resource_service['url']+"/"+platform_ID)
                    except:
                        pass
                    self.catalog.save()
                    result={"msg":output}
                    return json.dumps(result)
                else:
                    output="Platform '{}' not found ".format(platform_ID)
                    raise cherrypy.HTTPError("400 Resource not found.")
                print(output)
            else:
                raise cherrypy.HTTPError("{} {}".format(str(r_client.status_code),str(r_client.reason)))

        elif command=='removePatient':
            try:
                username=uri[1]
                platform_ID=uri[2]
                Patient_ID=uri[3]
            except:
                raise cherrypy.HTTPError("400 Bad Request! You need to specify parameters")

            r_client=requests.delete(clients_service['url']+"/removePatient/"+username+"/"+platform_ID+"/"+Patient_ID)
            if r_client.status_code==200:
                removedPatient=self.catalog.removePatient(platform_ID,Patient_ID)
                if removedPatient:
                    self.catalog.save()
                    output="Patient '{}' removed from platform '{}'. ".format(Patient_ID,platform_ID)
                    resource_service=self.catalog.retrieveService('resource_catalog')
                    try:
                        requests.delete(resource_service['url']+"/"+platform_ID+"/"+Patient_ID)
                    except:
                        pass
                    self.catalog.save()
                    result={"msg":output}
                    return json.dumps(result)
                else:
                    output="Can't remove Patient '{}' from platform '{}'. ".format(Patient_ID,platform_ID)
                    raise cherrypy.HTTPError("404 Resource not found")
                print(output)
            else:
                raise cherrypy.HTTPError("{} {}".format(str(r_client.status_code),str(r_client.reason)))
        else:
            raise cherrypy.HTTPError("501 No operation!")
   
if __name__ == '__main__':
    conf=sys.argv[1]
    db=sys.argv[2]
    ProfilesCatalog=catalogREST(conf,db)
    if ProfilesCatalog.service is not False:
        conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True
            }
        }
        cherrypy.tree.mount(ProfilesCatalog, ProfilesCatalog.service, conf)
        cherrypy.config.update({'server.socket_host': ProfilesCatalog.catalog.serviceIP})
        cherrypy.config.update({'server.socket_port': ProfilesCatalog.catalog.servicePort})
        cherrypy.engine.start()
        cherrypy.engine.block()
