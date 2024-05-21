import json, requests

class Generic_Service():
    def __init__(self, conf_fname,db_fname=False):
        self.conf_fname=conf_fname
        self.conf_content=json.load(open(self.conf_fname,"r"))
        self.service_name=self.conf_content['service_name']
        self.serviceCatalogAddress=self.conf_content['service_catalog']
        self.serviceIP=self.conf_content['IP_address']
        self.servicePort=self.conf_content['IP_port']
        if db_fname is not False:
            self.db_fname=db_fname
            self.db_content=json.load(open(self.db_fname,"r"))
            
    def registerRequest(self):
        msg={"service":self.service_name,"IP_address":self.serviceIP,"port":self.servicePort}
        try:
            service=requests.put(f'{self.serviceCatalogAddress}/register',json=msg).json()
            return service
        except:
            print("Failure in registration.")
            return False
    
    def retrieveService(self,service):
            request=requests.get(self.serviceCatalogAddress+'/'+service).json()
            return request
    
    def save(self):
        with open(self.db_fname,'w') as file:
            json.dump(self.db_content,file, indent=4)
    
        
        
        
        