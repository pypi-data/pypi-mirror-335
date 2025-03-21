from io import StringIO
import os
import yaml


from nosql_bulk_automation_package_tst.fileGenerator.QuotaGeneratorNew import QuotaGeneratorNew
from nosql_bulk_automation_package_tst.fileGenerator.NamespaceGenerator import NamespaceGenerator
from nosql_bulk_automation_package_tst.fileGenerator.ArgocdPhase import ArgocdPhase
import nosql_bulk_automation_package_tst.refernce_file_constants as refs


class CouchbaseExporterGenerator:
    
    def __init__(self):
        print('\n'+40*'#',end='\n\n')
        print("CouchbaseExporterGenerator")
        print('\n'+40*'#',end='\n\n')
        
    def couchbaseExporterGenerator(self,datastore,app,paas_name,sec_zone,phase,cid,reg,LZ):
        expId=cid
        truePhase=ArgocdPhase.get_phase(phase,paas_name.split('-'))
        exp_type='couchbase'
        sourcePath=f'{(datastore.lower())}/az/{LZ}/{reg}-{phase}-{cid}.yaml'
        print(sourcePath)
        ref_file= open(refs.cb_exporter_ref_file_path,'r')
        exp_file=ref_file.read()
        ref_file.close()
       
        exp_file=exp_file.replace("@datastore@/@provider@/@landing_zone@/@region@-@phase@-@cluster_name@.yaml",sourcePath)
        exp_file=exp_file.replace("@app@",app)
        exp_file=exp_file.replace("@phase@",phase)
        exp_file=exp_file.replace("@macroPhase@",truePhase)
        exp_file=exp_file.replace("@exporterId@",expId)
        exp_file=exp_file.replace("@region@",reg)
        exp_file=exp_file.replace("@application@",app)
        

        exp_filez = StringIO(exp_file)
        exp_content = yaml.load(exp_filez, Loader=yaml.Loader)
        if  sec_zone == 'cde':
            exp_content.update({"securityZone": "cde"})
            
        

    
        
        
        
        if not os.path.exists(f"dummyInventory/argocd-nosqlpaas-{truePhase}/{truePhase}/az/{paas_name}/{(datastore.lower())}-exporter"):
            os.makedirs(f"dummyInventory/argocd-nosqlpaas-{truePhase}/{truePhase}/az/{paas_name}/{(datastore.lower())}-exporter")
            print("The new exporter directory is created!")
        with open(f"dummyInventory/argocd-nosqlpaas-{truePhase}/{truePhase}/az/{paas_name}/{(datastore.lower())}-exporter/datastore-couchbase-exp-{app}-{reg}-{phase}-{cid}.yaml",'w+') as f:
            yaml.dump(exp_content,f,sort_keys=False)
            print("Exporter created succesfully")
        types='exp'
        if not os.path.exists(f"dummyInventory/argocd-nosqlpaas-{truePhase}/{truePhase}/az/{paas_name}/namespace/datastore-couchbase-exp-{app}.yaml"):
            print("Need to create the namespace")
            NamespaceGenerator().namespaceGenerator(datastore,app,paas_name,phase,types)
        else:
            print("Namespace alrady exists")
        
                
        ##generating Quota

        
        if not os.path.exists(f"dummyInventory/argocd-nosqlpaas-{truePhase}/{truePhase}/az/{paas_name}/quota/quota-{exp_type}.yaml"):
           print("quota need to be created")
        #    QuotaGenerator().quotaGenerator(app,paas_name,phase)
           QuotaGeneratorNew().quotaGenerator(exp_type.lower(),paas_name,phase)
        else:
            print("Quota already exists")


