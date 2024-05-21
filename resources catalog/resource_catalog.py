import json, requests, time, datetime, sys, threading, cherrypy
from etc.serverClass import *

class ResourcesServerREST(object):
    exposed=True
    def __init__(self,conf_fname,db_fname):
        self.catalog=ResourceService(conf_fname,db_fname) #file names
        self.service=self.catalog.registerRequest()            

    def GET(self,*uri,**params):
        uLen=len(uri)
        if uLen!=0:
            info=uri[0]
            if info=="platformsList":
                output=self.catalog.retrievePlatformsList()
            else:    
                platform= self.catalog.retrievePlatform(info)
                if platform is not False:
                    if uLen>1:
                        patientInfo= self.catalog.retrievePatientInfo(info,uri[1])
                        if patientInfo is not False:
                            if uLen>2:
                                deviceInfo=self.catalog.retrieveDeviceInfo(info,uri[1],uri[2])
                                if deviceInfo is not False:
                                    if uLen>3:
                                        output=deviceInfo.get(uri[3])
                                    elif len(params)!=0:
                                        parameter=str(params['parameter'])
                                        paramInfo=self.catalog.retrieveParameterInfo(info,uri[1],uri[2],parameter)
                                        if paramInfo is False:
                                            output=None
                                        else:
                                            output=paramInfo
                                    else:
                                        output=deviceInfo
                                else:
                                    output=patientInfo.get(uri[2])
                            elif len(params)!=0:
                                parameter=str(params['parameter'])
                                paramInfo=self.catalog.findParameter(info,uri[1],parameter)
                                if paramInfo is False:
                                    output=None
                                else:
                                    output=paramInfo
                            else:
                                output=patientInfo
                        else:
                            output=platform.get(uri[1])
                    else:
                        output=platform
                else:
                    output=self.catalog.db_content.get(info)
            if output==None:
                raise cherrypy.HTTPError(404,"Information Not found")
        else:
            output=self.catalog.db_content['description']
        return json.dumps(output) 

    def PUT(self,*uri):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        command=str(uri[0])
        saveFlag=False

        if command=="insertDevice":
            platform_ID=uri[1]
            patient_ID=uri[2]
            device=self.catalog.insertDevice(platform_ID,patient_ID,json_body)
            if device is False:
                raise cherrypy.HTTPError(404, "Resource not found!")
            else:
                saveFlag=True
        elif command=='addPatient':
            platform_ID=uri[1]
            patient_ID=json_body['patientID']
            #patient_name=json_body['patient_name']
            platformFlag=self.catalog.retrievePlatform(platform_ID)
            if platformFlag is False:
                requestClients=requests.get(self.catalog.serviceCatalogAddress+"/clients_catalog").json()
                if(requests.get(requestClients['url']+'/checkAssociation/'+platform_ID).json()["result"]):
                    patients=[]
                    newPlatform=self.catalog.insertPlatform(platform_ID,patients)
                else:
                    raise cherrypy.HTTPError("409 Platform Not valid")
                    
            self.catalog.addPatient(platform_ID,patient_ID,json_body)
            saveFlag=True
        else:
            raise cherrypy.HTTPError(501, "No operation!")
        if saveFlag:
            self.catalog.save()

    def DELETE(self,*uri):
        saveFlag=False
        uLen=len(uri)
        if uLen>0:
            platform_ID=uri[0]
            if uLen>1:
                patient_ID=uri[1]
                if uLen>2:
                    device_ID=uri[2]
                    removedDevice=self.catalog.removeDevice(platform_ID,patient_ID,device_ID)
                    if removedDevice:
                        output="Platform '{}' - Patient '{}' - Device '{}' removed".format(platform_ID,patient_ID,device_ID)
                        self.catalog.dateUpdate(self.catalog.retrievePatientInfo(platform_ID,patient_ID))
                        saveFlag=True
                    else:
                        output="Platform '{}'- Patient '{}' - Device '{}' not found ".format(platform_ID,patient_ID,device_ID)
                        raise cherrypy.HTTPError(404, "Resource not found!")
                else:
                    removedPatient=self.catalog.removePatient(platform_ID,patient_ID)
                    if removedPatient:
                        output="Platform '{}' - Patient '{}' removed".format(platform_ID,patient_ID)
                        saveFlag=True
                    else:
                        output="Platform '{}'- Patient '{}' not found ".format(platform_ID,patient_ID)
                        raise cherrypy.HTTPError(404, "Resource not found!")

            else:
                removedPlatform=self.catalog.removePlatform(platform_ID) 
                if removedPlatform:
                    output="Platform '{}' removed".format(platform_ID)
                    saveFlag=True
                else:
                    output="Platform '{}' not found ".format(platform_ID)
                    raise cherrypy.HTTPError(404, "Resource not found!")
        else:
            raise cherrypy.HTTPError(501, "No operation!")
        if saveFlag:
            self.catalog.save()
        print(output)
        return{"result":saveFlag}

class InactiveThread(threading.Thread):

    def __init__(self, ThreadID,catalog):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.catalog=catalog

    def run(self):
        while True:
            bot_url=self.catalog.retrieveService("telegram_bot")['url']
            for platform in self.catalog.db_content['platforms_list']:
                for patient in platform['patients']:
                    devices=patient['devices']
                    devicesCatalog=DevicesCatalog(devices)
                    dev_list=devicesCatalog.removeInactive(self.catalog.delta)
                    for dev in dev_list:
                        msg={"parameter":dev,"status":"REMOVED","tip":None}
                        requests.post(bot_url+'/warning/'+platform['platform_ID']+'/'+patient['patient_ID'], json=msg)
            self.catalog.save()
            time.sleep(self.catalog.delta)

if __name__ == '__main__':
    conf=sys.argv[1]
    db=sys.argv[2]
    server=ResourcesServerREST(conf,db)
    thread1=InactiveThread(1,server.catalog)
    thread1.start()
    time.sleep(1)
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(server, server.service, conf)
    cherrypy.config.update({'server.socket_host': server.catalog.serviceIP})
    cherrypy.config.update({'server.socket_port': server.catalog.servicePort})
    cherrypy.engine.start()
    #cherrypy.engine.block()