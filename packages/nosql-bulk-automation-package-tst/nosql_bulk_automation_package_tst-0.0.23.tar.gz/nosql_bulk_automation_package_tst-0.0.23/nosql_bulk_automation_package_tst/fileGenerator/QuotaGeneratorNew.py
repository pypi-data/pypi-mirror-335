from io import StringIO
import os
import yaml

from nosql_bulk_automation_package_tst.fileGenerator.ArgocdPhase import ArgocdPhase
import nosql_bulk_automation_package_tst.refernce_file_constants as refs

class QuotaGeneratorNew:
    
    def __init__(self):
        print('\n'+40*'#',end='\n\n')
        print("QuotaGenerator")
        print('\n'+40*'#',end='\n\n')
        
    def quotaGenerator(self,quota_type,paas_name,phase):
        truePhase=ArgocdPhase.get_phase(phase,paas_name.split('-'))
        macrophase=truePhase
        cred=truePhase
        # if phase in ['prd','ppt']:
        #     macrophase=cred='prd'
        if phase=='rnd':
            if 'ima' in paas_name:
                macrophase='rnd'
                cred='ima'
            else:
                macrophase=cred='rnd'
        # else:
        #     macrophase=cred='tst'
        quota_verison=''
        ref_file= open(refs.quota_ref_file_path,'r')
        quota_file=ref_file.read()
        ref_file.close()


        quota_file = quota_file.replace("@datastore@",quota_type)
        quota_file = quota_file.replace("@argocd_macrophase@",macrophase)
        quota_file = quota_file.replace("@macrophase@",cred)


        quota_filez = StringIO(quota_file)
        quota_content = yaml.load(quota_filez, Loader=yaml.Loader)
        print(yaml.dump(quota_content))
        path=f'dummyInventory/argocd-nosqlpaas-{truePhase}/{truePhase}/az/{paas_name}'
        if not os.path.exists(f"{path}/quota"):
            os.makedirs(f"{path}/quota")
            print("The new quota directory is created!")
        with open(f"{path}/quota/dbaas-{quota_type}.yaml",'w+') as f:
            yaml.dump(quota_content,f,sort_keys=False)
            print("quota created succesfully")

