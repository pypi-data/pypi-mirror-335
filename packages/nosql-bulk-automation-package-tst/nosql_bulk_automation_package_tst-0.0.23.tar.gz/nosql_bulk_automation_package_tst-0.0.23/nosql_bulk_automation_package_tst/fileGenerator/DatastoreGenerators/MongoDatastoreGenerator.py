import os
import yaml
import socket

class MongoDatastoreGenerator:

    def __init__(self):
        print('\n'+40*'#',end='\n\n')
        print("MongoDatastoreGenerator")
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
                         'firecell':( hosts.index(i)%3 + 1),
                        }
        return new_dict
    
    def setVars(self,vars,ops_url,phase,cid,reg):
        new_dict={}
        new_dict['id']=cid
        new_dict['phase']=vars['phase']
        new_dict['region']=reg
        new_dict['type']='mongodb'
        pool_name=cid.split('-')[0]
        new_dict['pool_name']=pool_name
        new_dict['nanoUuid']='24e948d9-5bc6-11e7-a4b8-0050560c4716'
        new_dict['ops-manager']={}
        try:
            if vars['peak']:
                cName=vars['phase']+'-'+vars['id']+'-'+vars['peak']
            else:
                cName=vars['phase']+'-'+vars['id']
        except:
            cName=vars['phase']+'-'+vars['id']
        new_dict['ops-manager']['clusterName']=cName
        new_dict['ops-manager']['group']=(f'{reg}-{phase}-{cid}').upper()
        ph=''
        url=''
        if phase not in ['prd','ppt'] and 'mms' not in vars['id']:
            ph='tst'
        elif 'mms' in vars['id']:
            ph='master'
        else:
            ph='prd'
        new_dict['ops-manager']['phase']=ph
        new_dict['ops-manager']['url']=ops_url
        new_dict['ops-manager']['provider']="public"
        new_dict['k8s-services']={}
        new_dict['k8s-services'].update({f'{pool_name}':{'name':pool_name}})
        
        return new_dict,ph


    def datastoreGenerator(self,hosts,vars,ops_url,phase,cid,reg,LZ):

        datastore_file={'datastore':{}}
        datastore_file['datastore']['hosts']=dict()
        datastore_file['datastore']['vars']=dict()
        datastore_file['datastore']['kv2secret']=dict()
        datastore_file['datastore']['mode']=dict()
       

        ##setting hosts

        datastore_file['datastore']['hosts']=self.setHosts(hosts,phase)

        ###setting vars

        datastore_file['datastore']['vars'],ph=self.setVars(vars,ops_url,phase,cid,reg)

        datastore_file['datastore']['kv2secret']['keyvaults']={}
        datastore_file['datastore']['kv2secret']['keyvaults']['tenantId']='7d7761c0-8b7a-49bb-8975-a6aa1be7c38b'
        if ph=='master':
            KV='ama-mdb-ccp-49h4wbsx0nnn'
        elif ph=='prd':
            KV='ama-mdb-ccp-tadundatihnw'
        else:
            KV='ama-mdb-ccp-uax2567nwelf'
        datastore_file['datastore']['kv2secret']['keyvaults']['name']=KV
        datastore_file['datastore'].update({'mode':{'acn':{'endpointsAsFQDN':True}}})
        
        print(yaml.safe_dump(datastore_file))

        isExist = os.path.exists(f"dummyInventory/datastores/mongodb/az/{LZ}")
        if not isExist:
            os.makedirs(f"dummyInventory/datastores/mongodb/az/{LZ}")
            print("The new directory is created!")
        with open(f'dummyInventory/datastores/mongodb/az/{LZ}/{reg}-{phase}-{cid}.yaml', 'w+') as f:
            yaml.dump(datastore_file,f,sort_keys=False)
            print("datastore file created successfully")