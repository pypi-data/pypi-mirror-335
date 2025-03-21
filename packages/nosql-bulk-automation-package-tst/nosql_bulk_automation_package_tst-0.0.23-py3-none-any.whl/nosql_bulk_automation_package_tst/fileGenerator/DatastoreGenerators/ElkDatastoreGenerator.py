import os
import yaml
import socket
import importlib.resources as pkg_resources

import nosql_bulk_automation_package_tst

class ElkDatastoreGenerator:

    def __init__(self):
        print('\n'+40*'#',end='\n\n')
        print("ElkDatastoreGenerator")
        print('\n'+40*'#',end='\n\n')
    def setIpAddress(self,hostAdd):
        try:
            return socket.gethostbyname(hostAdd)
        except:
            print("the  host address",hostAdd," is incrroect")
            exit(0)

    def setHosts(self,hosts,phase):
        new_dict={}
        check=set()
        firecells=set()
        for i in hosts:
            new_dict[i]={'ip':self.setIpAddress(i),
                         'firecell':( 1 if hosts.index(i)%2==0 else 2),
                        }
            
            if hosts.index(i)<=(1 if phase not in ['prd','ppt'] else 2):
                new_dict[i].update({'prometheus':True})

        
        return new_dict
    
    def setVars(self,app,paas_name,sec_zone,phase,cid,reg,size):
        new_dict={}
        new_dict['id']=cid
        new_dict['phase']=phase
        new_dict['region']=reg
        new_dict['type']='elasticsearch'
        size_dict={}
        # if size=='S':
        #     size_dict={ 'memoryLimit':'50Mi',
        #                 'memoryRequest':'32Mi',
        #                 'cpuRequest':'30m'}
        # elif size=='M':
        #     size_dict={ 'memoryLimit':'200Mi',
        #                 'memoryRequest':'100Mi',
        #                 'cpuRequest':'50m'}
        # else :
        #     size_dict={ 'memoryLimit':'400Mi',
        #                 'memoryRequest':'200Mi',
        #                 'cpuRequest':'100m'}
        # new_dict.update(size_dict)
        
        elk_yaml_path = pkg_resources.files(nosql_bulk_automation_package_tst).joinpath("fileGenerator/sizings/elk_sizing.yaml")
        with open(elk_yaml_path, 'r') as file:
            size_data = yaml.safe_load(file)
    
        # Get sizing data
        sizings = size_data.get('sizings', {})
        print(sizings)
        # Check if the size exists in the sizings dictionary
        if size in sizings:
            size_dict = sizings[size]
            print(sizings[size])
            type(size_dict)
            new_dict.update(size_dict)
        else:
            print(f"Size '{size}' not found in the YAML configuration.")
        
        # new_dict.update(size_dict)
        return new_dict


    def datastoreGenerator(self,hosts,app,paas_name,sec_zone,phase,cid,reg,LZ,size):

        datastore_file={'datastore':{}}
        datastore_file['datastore']['hosts']=dict()
        datastore_file['datastore']['vars']=dict()
        datastore_file['docker']=dict()
       

        ##setting hosts

        datastore_file['datastore']['hosts']=self.setHosts(hosts,phase)

        ###setting vars

        datastore_file['datastore']['vars']=self.setVars(app,paas_name,sec_zone,phase,cid,reg,size)

        ##Ssetting docker

        datastore_file['docker']={'registryType':"adp",'tag':"v1.3.0"}
        print(yaml.safe_dump(datastore_file))

        isExist = os.path.exists(f"dummyInventory/datastores/elasticsearch/az/{LZ}")
        if not isExist:
            os.makedirs(f"dummyInventory/datastores/elasticsearch//az/{LZ}")
            print("The new directory is created!")
        with open(f'dummyInventory/datastores/elasticsearch/az/{LZ}/{reg}-{phase}-{cid}.yaml', 'w+') as f:
            yaml.dump(datastore_file,f,sort_keys=False)
            print("datastore file created successfully")