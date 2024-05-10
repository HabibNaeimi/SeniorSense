import cherrypy
import json
import requests
import time
import sys

from etc.service_class import ServiceCatalog

    
class ServiceCatalogREST():
    exposed=True
    def __init__(self,filename):
        self.catalog=Service_Catalog(filename)
                
    def GET(self,*uri):
        if len(uri)!=0:
            if len(uri)==2:
                if uri[1]=='public':
                    try:
                        url=requests.get(self.catalog.content['ngrok']+"/api/tunnels/"+uri[0]).json()['public_url']
                        url=url+self.catalog.content[str(uri[0])]['service']
                        output={
                            "url":url
                            }
                    except:
                        try:
                            output={
                                "url":self.catalog.content[str(uri[0])]['url']
                                }
                        except:
                            raise cherrypy.HTTPError(404,"The requested service was not found")
                else:
                    raise cherrypy.HTTPError(400, "Bad request")

            else: 
                try:
                    output=self.catalog.content[str(uri[0])]
                except:
                    raise cherrypy.HTTPError(404,"The requested service was not found")
        else:
            output=self.catalog.content['overview'] 

        return json.dumps(output,indent=4) 

    def PUT(self,*uri):
        Flag=0
        if len(uri)!=0:
            if uri[0]=="register":
                try:
                    try:
                        body=cherrypy.request.body.read()
                        json_body=json.loads(body.decode('utf-8'))
                    except:
                        raise cherrypy.HTTPError(400, "It's not possible to read your body message!")
                    new_service=self.catalog.record(json_body['service'],json_body['IP_address'],json_body['port'])
                    if new_service is not False:
                        output="Service '{}' updated".format(json_body['service'])
                        Flag=1
                    else:
                        output="Service '{}'- Registration failed".format(json_body['service'])
                except IndexError as e:
                    #print(e)
                    raise cherrypy.HTTPError(500, "Internal error: can't process your request!")
                    output="Error request."
            else:
                raise cherrypy.HTTPError(501, "No operation!")
        print(output)
        if Flag==1:
            self.catalog.save()
            return json.dumps(new_service,indent=4)
        
    def DELETE(self,*uri):
        if len(uri)!=0:
            try:
                if self.catalog.deleteService(uri[0]):
                    print("Service '{}' removed".format(uri[0]))
                    self.catalog.save()
                else:
                    raise cherrypy.HTTPError(404, "Service not found: "+uri[0])
                    
            except IndexError as e:
                raise cherrypy.HTTPError(500, "Internal error: can't process your request!")
                print("Error request.")
            

if __name__ == '__main__':
    settings=sys.argv[1]
    serviceCatalog=ServiceCatalogREST(settings)
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(serviceCatalog, serviceCatalog.catalog.service, conf)
    cherrypy.config.update({'server.socket_host': serviceCatalog.catalog.serviceCatalogIP})
    cherrypy.config.update({'server.socket_port': serviceCatalog.catalog.serviceCatalogPort})
    cherrypy.engine.start()
    while True:
        time.sleep(1)
    cherrypy.engine.block()

