from io import StringIO
import os
import yaml

from nosql_bulk_automation_package_tst.fileGenerator.ArgocdPhase import ArgocdPhase
import nosql_bulk_automation_package_tst.refernce_file_constants as refs


class NamespaceGenerator:
    def __init__(self):
        print('\n'+40*'#',end='\n\n')
        print('NamespaceGenerator')
        print('\n'+40*'#',end='\n\n')
    
    def datastore_nano_id(self,datastore):
        if datastore == 'couchbase':
            return '24e948d1-5bc6-11e7-a4b8-0050560c4716'
        elif datastore == 'mongodb':
            return '24e948d9-5bc6-11e7-a4b8-0050560c4716'
        elif datastore == 'Elasticsearch':
            return '24e996f8-5bc6-11e7-a4b8-0050560c4716'
        else:
            print("error : no matching datasore nano in namespace")
            exit(0)
        
    def namespaceGenerator(self,datastore,app,paas_name,phase,types):

        dc_prov="az"
        secZone="tnz"
        calico = 'false'

        ns_file={}
        truePhase=ArgocdPhase.get_phase(phase,paas_name.split('-'))
        # ns_phase='prd' if phase in ['prd','ppt','ccp'] else 'tst'
        ns_phase=truePhase
 
        ns_version=''
        ref_file_path = refs.namespace_ref_file_path.replace("@type@", types)
        
        # ref_file= open(f"../reference/{(datastore.lower())}-exporter/@namespace@-@region@-@phase@-@exporterId@.yaml",'r')
        ref_files= open(ref_file_path,'r')
        # ref_file=yaml.safe_load(ref_file)
        namespace_file=ref_files.read()
        ref_files.close()

        if datastore=='Elasticsearch':
            ns_type='Elasticsearch'
            ns='elk'
        elif datastore=="Couchbase":
            ns_type='couchbase'
            ns='couchbase'
        else:
            ns_type='mongodb'
            ns='mongodb'
        # ns_file['name']=f'datastore-{ns}-{types}-{app}'
        if paas_name in ["nld10","nld7","nld8","nld9","prd-we-tcp01","prd-we-tcp02","tst-we-cytr01","eus1","eus2","eus3","eus4"]:
            calico='true'
        else:
           calico='false'
        namespace_file = namespace_file.replace("app.kubernetes.io/part-of: @datastore@",f"app.kubernetes.io/part-of: {ns_type}")
        namespace_file = namespace_file.replace("@app@",app)
        namespace_file = namespace_file.replace("dbaas-@datastore@",f'dbaas-{ns}')
        namespace_file = namespace_file.replace("@datastore@",ns)
        namespace_file = namespace_file.replace("@calico@",calico)
        namespace_file = namespace_file.replace("@provider@",'az')
        namespace_file = namespace_file.replace("@macrophase@",ns_phase)
        namespace_file = namespace_file.replace("@datastoreNanoID@",self.datastore_nano_id(ns_type))
        namespace_file = namespace_file.replace("@securityZone@",secZone)
        namespace_file = namespace_file.replace("@paas_name@",paas_name)
        
        namespace_filez = StringIO(namespace_file)
        namespace_content = yaml.load(namespace_filez, Loader=yaml.Loader)
        if  namespace_content['calico'] == 'true':
            namespace_content.update({"JenkinsNamespace": "datastore-tools"})
        
        path=f'dummyInventory/argocd-nosqlpaas-{truePhase}/{truePhase}/az/{paas_name}'
        if not os.path.exists(f"{path}/namespace"):
            os.makedirs(f"{path}/namespace")
            print("The new namespace directory is created!")
        with open(f'{path}/namespace/datastore-{ns}-{types}-{app}.yaml', 'w+',) as f :
            yaml.dump(namespace_content,f,sort_keys=False)
        print("Namespace created succesfully")

        
