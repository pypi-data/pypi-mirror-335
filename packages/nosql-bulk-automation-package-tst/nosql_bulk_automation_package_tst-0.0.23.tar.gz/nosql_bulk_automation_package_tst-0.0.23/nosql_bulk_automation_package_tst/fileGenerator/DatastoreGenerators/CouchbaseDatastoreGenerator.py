import os
import yaml
import socket
import importlib.resources as pkg_resources
import nosql_bulk_automation_package_tst

class CouchbaseDatastoreGenerator:

    def __init__(self):
        print('\n'+40*'#',end='\n\n')
        print("CouchbaseDatastoreGenerator")
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
    

    def set_k8services(self,k8s,reg,pool):
        k8services={}
        for name in k8s:
                bucketName=(name.lower()).replace("_","-")
                for accessTypeShortName in ['kv','n1']:
                    
                    keys='-'.join(list(filter(None,[reg,pool,bucketName,accessTypeShortName])))
                    if accessTypeShortName=='kv':
                        accessType='KEY_VALUE'
                    if accessTypeShortName=='n1':
                        accessType='N1QL'
                    k8services[keys]={}
                    k8services[keys]['access_type']=accessType
                    k8services[keys]['cluster_namespace']=name
        print(k8services)

        return k8services

    def setVars(self,k8s,phase,cid,reg,size):
        new_dict={}
        new_dict['id']=cid
        new_dict['phase']=phase
        new_dict['region']=reg
        new_dict['type']='couchbase'
        pool_name=cid.split('-')[0]
        new_dict['pool_name']=pool_name
        new_dict['nanoUuid']='nanoUuid'
        new_dict['ports']={}
        new_dict['ports']['admin']=8091
        new_dict['ports']['admin-ssl']= 18091
        new_dict['ports']['data']= 11210
        new_dict['ports']['data-ssl']= 11207
        new_dict['ports']['n1ql']= 8093
        new_dict['ports']['n1ql-ssl']= 18093
    
        #k8services
        new_dict['k8s-services']={}
        new_dict['k8s-services']=self.set_k8services(k8s,reg,pool_name)

        #memory setting

        size_dict={}
        # exit(0)
        cb_yaml_path = pkg_resources.files(nosql_bulk_automation_package_tst).joinpath("fileGenerator/sizings/cb_sizing.yaml")
        with open(cb_yaml_path, 'r') as file:
            size_data = yaml.safe_load(file)
    
        # Get sizing data
        sizings = size_data.get('sizings', {})

        # Check if the size exists in the sizings dictionary
        if size in sizings:
            size_dict = sizings[size]
            type(size_dict)
            new_dict.update(size_dict)
        else:
            print(f"Size '{size}' not found in the YAML configuration.")
        
        # new_dict.update(size_dict)
        return new_dict
       


    def datastoreGenerator(self,hosts,vars,size,k8s,phase,cid,reg,LZ):

        datastore_file={'datastore':{}}
        datastore_file['datastore']['hosts']=dict()
        datastore_file['datastore']['vars']=dict()
        datastore_file['datastore']['mode']=dict()
       

        ##setting hosts

        datastore_file['datastore']['hosts']=self.setHosts(hosts,phase)

        ###setting vars

        datastore_file['datastore']['vars']=self.setVars(k8s,phase,cid,reg,size)
        datastore_file['datastore'].update({'mode':{'acn':{'endpointsAsFQDN':True}}})
        
        print(yaml.safe_dump(datastore_file))

        isExist = os.path.exists(f"dummyInventory/datastores/couchbase/az/{LZ}")
        if not isExist:
            os.makedirs(f"dummyInventory/datastores/couchbase/az/{LZ}")
            print("The new directory is created!")
        with open(f'dummyInventory/datastores/couchbase/az/{LZ}/{reg}-{phase}-{cid}.yaml', 'w+') as f:
            yaml.dump(datastore_file,f,sort_keys=False)
            print("datastore file created successfully")