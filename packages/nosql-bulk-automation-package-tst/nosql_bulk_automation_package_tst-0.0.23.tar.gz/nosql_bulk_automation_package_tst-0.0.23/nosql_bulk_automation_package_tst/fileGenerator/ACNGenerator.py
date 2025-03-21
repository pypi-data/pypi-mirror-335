from io import StringIO
import os
import yaml
import importlib.resources as pkg_resources


import nosql_bulk_automation_package_tst
from nosql_bulk_automation_package_tst.fileGenerator.QuotaGeneratorNew import QuotaGeneratorNew
from nosql_bulk_automation_package_tst.fileGenerator.NamespaceGenerator import NamespaceGenerator
from nosql_bulk_automation_package_tst.fileGenerator.ACNServiceGenerator import ACNServiceGenerator
from nosql_bulk_automation_package_tst.fileGenerator.ArgocdPhase import ArgocdPhase
import nosql_bulk_automation_package_tst.refernce_file_constants as refs

class ACNGenerator:
    
    def __init__(self):
        print('\n'+40*'#',end='\n\n')
        print("ACNGenerator")
        print('\n'+40*'#',end='\n\n')
        
    def acnGenerator(self,datastore,app,paas_name,sec_zone,phase,cid,reg,LZ,size):
        
        ref_file= open(refs.acn_ref_file_path,'r')
        acn_file=ref_file.read()
        ref_file.close()
        
        if datastore=='Elasticsearch':
            pass
        else:
           
            acn='acn'
            sourcePath=f'{(datastore.lower())}/az/{LZ}/{reg}-{phase}-{cid}.yaml'
            acn_yaml_path = pkg_resources.files(nosql_bulk_automation_package_tst).joinpath("fileGenerator/sizings/acn_sizing.yaml")
            with open(acn_yaml_path, 'r') as file:
                size_data = yaml.safe_load(file)
    
            # Get sizing data
            sizings = size_data.get('sizings', {})

            # Check if the size exists in the sizings dictionary
            if size in sizings:
                size_dict = sizings[size]
            else:
                print(f"Size '{size}' not found in the YAML configuration.")
            
            
            acn_file = acn_file.replace("@app@",app)
            acn_file = acn_file.replace("@datastore@",datastore.lower())
            acn_file = acn_file.replace("@phase@",phase)
            acn_file = acn_file.replace("@securityZone@",sec_zone)
            acn_file = acn_file.replace("@manager_memory_request@",size_dict["memoryRequest"])
            acn_file = acn_file.replace("@manager_memory_limit@",size_dict["memoryLimit"])
            acn_filez = StringIO(acn_file)
            acn_content = yaml.load(acn_filez, Loader=yaml.Loader)
            truePhase=ArgocdPhase.get_phase(phase,paas_name.split('-'))
            print(yaml.dump(acn_content))
            if not os.path.exists(f"dummyInventory/argocd-nosqlpaas-{truePhase}/{truePhase}/az/{paas_name}/acn"):
                os.makedirs(f"dummyInventory/argocd-nosqlpaas-{truePhase}/{truePhase}/az/{paas_name}/acn")
                print("The new acn directory is created!")
            with open(f"dummyInventory/argocd-nosqlpaas-{truePhase}/{truePhase}/az/{paas_name}/acn/datastore-{datastore.lower()}-acn-{app}-{phase}-{app}.yaml",'w+') as f:
                yaml.dump(acn_content,f,sort_keys=False)
                print("ACN created succesfully")
            types='acn'

            ##geenrating ACN-Serivces

            ACNServiceGenerator().acnServiceGenerator(datastore,app,paas_name,sec_zone,phase,cid,reg,LZ)
            


            if not os.path.exists(f"dummyInventory/argocd-nosqlpaas-{truePhase}/{truePhase}/az/{paas_name}/namespace/datastore-{datastore.lower()}-acn-{app}.yaml"):
                print("Need to create the namespace")
                NamespaceGenerator().namespaceGenerator(datastore,app,paas_name,phase,types)
            else:
                print("Namespace alrady exists")
            
                    
            ##generating Quota

            
            if not os.path.exists(f"dummyInventory/argocd-nosqlpaas-{truePhase}/{truePhase}/az/{paas_name}/quota/quota-{app}.yaml"):
                print("quota need to be created")
                # QuotaGenerator().quotaGenerator(app,paas_name,phase)
                QuotaGeneratorNew().quotaGenerator((datastore.lower()),paas_name,phase)
            else:
                print("Quota already exists")


