from io import StringIO
import os
import yaml
import fileinput


from nosql_bulk_automation_package_tst.fileGenerator.NamespaceGenerator import NamespaceGenerator
from nosql_bulk_automation_package_tst.fileGenerator.ArgocdPhase import ArgocdPhase
import nosql_bulk_automation_package_tst.refernce_file_constants as refs

class ACNServiceGenerator:
    
    def __init__(self):
        print('\n'+40*'#',end='\n\n')
        print("ACNServiceGenerator")
        print('\n'+40*'#',end='\n\n')
    def acnServiceGenerator(self,datastore,app,paas_name,sec_zone,phase,cid,reg,LZ):
        
        truePhase=ArgocdPhase.get_phase(phase,paas_name.split('-'))
        ref_file= open(refs.acns_ref_file_path,'r')
        acn_services_file=ref_file.read()
        ref_file.close()
        if datastore=='Elasticsearch':
            pass
        else:

            sourcePath=f'{(datastore.lower())}/az/{LZ}/{reg}-{phase}-{cid}.yaml'
            acn_services_file = acn_services_file.replace("@datastore@",datastore.lower())
            acn_services_file = acn_services_file.replace("@app@",app)
            acn_services_file = acn_services_file.replace("@phase@",phase)
            
            # acn_services_file[acnServices]['application']=app
            # acn_services_file[acnServices]['namespace']=f"datastore-{(datastore.lower())}-acn-{app}"
            # acn_services_file[acnServices]['version']=version
            # acn_services_file[acnServices]['phase']=phase
            # acn_services_file[acnServices]['datastore']=datastore.lower()
            # acn_services_file[acnServices]['sources']=[]
            # acn_services_file[acnServices]['sources'].append(sourcePath)
            
            
            acns_filez = StringIO(acn_services_file)
            acns_content = yaml.load(acns_filez, Loader=yaml.Loader)
            
            
            del acns_content["acnServices"]["sources"]
            acns_content["acnServices"]['sources']=[]
            acns_content["acnServices"]['sources'].append(sourcePath)
            
            
            #########################################################################################
            # here the ACN is different approch than others as ACN have the sources like a stack#####            
            #########################################################################################

            paths=f"nosql-paas-inventory/inventory/argocd-nosqlpaas-{truePhase}/{truePhase}/az/{paas_name}/acn-services"
            dummy_inv_path = f"dummyInventory/argocd-nosqlpaas-{truePhase}/{truePhase}/az/{paas_name}/acn-services"
            if not os.path.exists(f"{dummy_inv_path}"):
                os.makedirs(f"{dummy_inv_path}")
                print("The new acn-services directory is created!")
            try:
                with open(f"{paths}/datastore-{datastore.lower()}-acn-{app}-{phase}-{app}.yaml",'r+') as f:
                    file=yaml.safe_load(f)
                    print(file)
                    if sourcePath not in file['acnServices']['sources']:
                        print("this is already present in the ACN serives so no need to add..")
                        file['acnServices']['sources'].append(sourcePath)
                    # yaml.dump(file,f,sort_keys=False)
                        with open(f"{dummy_inv_path}/datastore-{datastore.lower()}-acn-{app}-{phase}-{app}.yaml","w+") as f1:
                            yaml.dump(file,f1,sort_keys=False)
            except IOError:
                print("ACNS not found need to create new ancs file")
                with open(f"{dummy_inv_path}/datastore-{datastore.lower()}-acn-{app}-{phase}-{app}.yaml","w+") as f:
                    yaml.dump(acns_content,f,sort_keys=False)
            print(yaml.dump(acns_content))