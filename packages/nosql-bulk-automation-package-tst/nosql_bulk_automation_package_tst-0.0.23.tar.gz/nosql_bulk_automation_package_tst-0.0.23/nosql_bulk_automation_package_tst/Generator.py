import os
import yaml
import json

from nosql_bulk_automation_package_tst.fileGenerator.ExporterFileGenerators.MongoDBExporterGenerator import MongoDBExporterGenerator
from nosql_bulk_automation_package_tst.fileGenerator.ExporterFileGenerators.CouchbaseExporterGenerator import CouchbaseExporterGenerator
from nosql_bulk_automation_package_tst.fileGenerator.ExporterFileGenerators.ElasticsearchExporterGenerator import ElasticsearchExporterGenerator
from nosql_bulk_automation_package_tst.fileGenerator.DatastoreGenerators.ElkDatastoreGenerator import ElkDatastoreGenerator
from nosql_bulk_automation_package_tst.fileGenerator.DatastoreGenerators.MongoDatastoreGenerator import MongoDatastoreGenerator
from nosql_bulk_automation_package_tst.fileGenerator.DatastoreGenerators.CouchbaseDatastoreGenerator import CouchbaseDatastoreGenerator
from nosql_bulk_automation_package_tst.fileGenerator.ACNGenerator import ACNGenerator
from nosql_bulk_automation_package_tst.fileGenerator.NamespaceGenerator import NamespaceGenerator



class Generator:
    def __init__(self):
        print("in Generator")
    
    def get_dns_name(self,path,app):

        with open(path,'r') as file:
            data=yaml.safe_load(file)
        print(data['azure_resourcegroup'].split('-'))
        if app in data['azure_resourcegroup'].split('-'):
            print("true")
        else:
            print("app name given in excel sheet and in IaaS inventory was not matches")
            exit(0)
        return data['dns_zone_name']
    
    def get_ops_url(self,path):

        with open(path,'r') as file:
            data=yaml.safe_load(file)
        print(data['om_base_url'].split('/')[0])
        return data['om_base_url'].split('.net')[0]+'.net'
    

    
    def get_ELK_Hosts(self,phase,cid,reg):
        regions={'we': 'eu-w', 'ne': 'eu-n', 'eus2': 'usa-e2', 'wus2': 'usa-w2',
                  'gwc': 'deu-wc', 'fc': 'fra-c'}
        try:
            region=regions.get(reg)
            print(region)
        except:
            print("region not valid")
        # try:
        #     try:
        #         file_path=f'els-prometheus-environments/inventory/az/{region}/elasticsearch/inventory/{phase}/{phase}-{cid}.yml'
        #         if not os.path.exists(file_path):
        #             raise FileNotFoundError
        #     except:
        #         file_path=f'els-prometheus-environments/inventory/az/{region}/elasticsearch/inventory/{phase}/{reg}-{phase}-{cid}.yml'
        #     if not os.path.exists(file_path):
        #             raise FileNotFoundError
        # except:
        #     try:
        #         file_path=f'els-prometheus-environments/inventory/az/{region}/elasticsearch/inventory/{phase}/{phase}-{cid}.yaml'
        #         if not os.path.exists(file_path):
        #             raise FileNotFoundError
        #     except:
        #         file_path=f'els-prometheus-environments/inventory/az/{region}/elasticsearch/inventory/{phase}/{reg}-{phase}-{cid}.yaml'
        #         try:
        #             if not os.path.exists(file_path):
        #                 raise FileNotFoundError
        #         except:
        #             print(f"elastic cluster not found in thsi path {file_path}")
        
        file_paths = [
                f'els-prometheus-environments/inventory/az/{region}/elasticsearch/inventory/{phase}/{phase}-{cid}.yml',
                f'els-prometheus-environments/inventory/az/{region}/elasticsearch/inventory/{phase}/{reg}-{phase}-{cid}.yml',
                f'els-prometheus-environments/inventory/az/{region}/elasticsearch/inventory/{phase}/{phase}-{cid}.yaml',
                f'els-prometheus-environments/inventory/az/{region}/elasticsearch/inventory/{phase}/{reg}-{phase}-{cid}.yaml'
            ]

# Try each file path
        for file_path in file_paths:
            if os.path.exists(file_path):
                print(f"File found: {file_path}")
                break
        else:
            print(f"Elastic cluster not found in any of the paths: {file_paths}")
        with open(file_path,'r') as file:
            data=yaml.safe_load(file)
        # print(data[f'{phase}-{cid}'].get('hosts',{}).values())
        hosts=[]
        try:
            for host in data[f'{phase}-{cid}'].get('hosts',{}).values():
                if 'ansible_host' in host:
                    hosts.append(host['ansible_host'])
        except:
            for host in data[f'{reg}-{phase}-{cid}'].get('hosts',{}).values():         
                if 'ansible_host' in host:
                    hosts.append(host['ansible_host'])
        return hosts



    def get_MONGO_Hosts_and_Vars(self,app,phase,cid,reg,LZ):
        
        regions={'we': 'eu-w', 'ne': 'eu-n', 'eus2': 'usa-e2', 'wus2': 'usa-w2',
                  'gwc': 'deu-wc', 'fc': 'fra-c'}
        try:
            region=regions.get(reg)
            print(region)
        except:
            print("region not valid")    
        file_path=f'mongodb-ansible-blueprints/mdb/az/{region}/{LZ}'
        dns=self.get_dns_name(file_path+f'/group_vars/{reg}-{phase}-{cid}/main.yaml',app)
        ops_url=self.get_ops_url(file_path+f'/group_vars/{reg}-{phase}-{cid}/main.yaml')
        print(dns)
        file_path=f'{file_path}/{reg}-{phase}-{cid}.yaml'
        with open(file_path,'r') as file:
            data=yaml.safe_load(file)
        print(data[f'{reg}-{phase}-{cid}'].get('hosts',{}).keys())
        hosts=[]
        for host in data[f'{reg}-{phase}-{cid}'].get('hosts',{}).keys():
            hosts.append(host+'.'+dns)
        vars=data[f'{reg}-{phase}-{cid}'].get('vars',{})

        return [hosts,vars,ops_url]
    

    def get_k8services(self,path):
        with open(path,'r') as file:
            data=json.load(file)
        buckets=[]
        for bucket in data['buckets']:
            buckets.append(bucket['name'])
        print(buckets)
        return buckets

    def get_Couchbase_Hosts_and_Vars(self,app,phase,cid,reg,LZ):
            
        regions={'we': 'eu-w', 'ne': 'eu-n', 'eus2': 'usa-e2', 'wus2': 'usa-w2',
                'gwc': 'deu-wc', 'fc': 'fra-c'}
        try:
            region=regions.get(reg)
            print(region)
        except:
            print("region not valid")    
        file_path=f'couchbase-inventory/az/{region}/{LZ}'
        # k8s=self.get_k8services(file_path+f'/group_vars/{phase}-{cid}/{phase}-{cid}_public.json')
        try:
            try:
                try:
                    dns=self.get_dns_name(file_path+f'/group_vars/{reg}-{phase}-{cid}/{reg}-{phase}-{cid}_infra.yml',app)
                except:
                    dns=self.get_dns_name(file_path+f'/group_vars/{reg}-{phase}-{cid}/{reg}-{phase}-{cid}_infra.yaml',app)
                k8s=self.get_k8services(file_path+f'/group_vars/{reg}-{phase}-{cid}/{reg}-{phase}-{cid}_public.json')
                try:
                    file_path=f'{file_path}/{reg}-{phase}-{cid}.yml'
                except:
                    file_path=f'{file_path}/{reg}-{phase}-{cid}.yaml'
            except:
                try:
                    dns=self.get_dns_name(file_path+f'/group_vars/{phase}-{cid}/{phase}-{cid}_infra.yml',app)
                except:
                    dns=self.get_dns_name(file_path+f'/group_vars/{phase}-{cid}/{phase}-{cid}_infra.yaml',app)
                k8s=self.get_k8services(file_path+f'/group_vars/{phase}-{cid}/{phase}-{cid}_public.json')
                try:
                    file_path=f'{file_path}/{phase}-{cid}.yml'
                except:
                    file_path=f'{file_path}/{phase}-{cid}.yaml'
        except Exception as e:
            print(e)
            print("the cluster details not found in couchbase IaaS inventory")
            exit(0)
        print(dns)
        
        with open(file_path,'r') as file:
            data=yaml.safe_load(file)
        try:
            try:
                if data[f'{reg}-{phase}-{cid}']:
                    cluster=f'{reg}-{phase}-{cid}'
            except:
                    cluster=f'{phase}-{cid}'
        except:
            pass
        
        print(data[cluster].get('hosts',{}).keys())
        hosts=[]
        for host in data[cluster].get('hosts',{}).keys():
            hosts.append(host+'.'+dns)
        vars=data[cluster].get('vars',{})
        # print(*hosts,*vars,sep='\n')
        print(k8s)
        return [hosts,vars,k8s]




    def parameters(self,parms):
        datastore,app,paas_name,sec_zone,phase,cid,reg,LZ,size=[parms[i] for i in range(len(parms))]
        print(datastore,app,paas_name,sec_zone,phase,cid,reg,LZ,size,sep='\n')

        #calling the repo to fetch the hosts
        ### generating the datastore-file 
        if datastore=='Elasticsearch':
            hosts=self.get_ELK_Hosts(phase,cid,reg)
            ElkDatastoreGenerator().datastoreGenerator(hosts,app,paas_name,sec_zone,phase,cid,reg,LZ,size)
            ElasticsearchExporterGenerator().elasticsearchExporterGenerator(datastore,app,paas_name,sec_zone,phase,cid,reg,LZ)
        elif datastore=='Mongodb':
            hosts,vars,ops_url=self.get_MONGO_Hosts_and_Vars(app,phase,cid,reg,LZ)
            MongoDatastoreGenerator().datastoreGenerator(hosts,vars,ops_url,phase,cid,reg,LZ)
            MongoDBExporterGenerator().mongodbExporterGenerator(datastore,app,paas_name,sec_zone,phase,cid,reg,LZ)
        else:
            hosts,vars,k8s=self.get_Couchbase_Hosts_and_Vars(app,phase,cid,reg,LZ)
            CouchbaseDatastoreGenerator().datastoreGenerator(hosts,vars,size,k8s,phase,cid,reg,LZ)
            CouchbaseExporterGenerator().couchbaseExporterGenerator(datastore,app,paas_name,sec_zone,phase,cid,reg,LZ)
        # print(*hosts,sep='\n')

  
        
       

        ##generating Exporter files

        # ExporterGenerator().exporterGenerator(datastore,app,paas_name,sec_zone,phase,cid,reg,LZ)
        ACNGenerator().acnGenerator(datastore,app,paas_name,sec_zone,phase,cid,reg,LZ,size)


        print("all resources got created for ",reg,'-',phase,'-', cid," in ",paas_name,sep='')


    def parameters(self,datastore,app,paas_name,sec_zone,phase,cid,reg,LZ,size,):
        # datastore,app,paas_name,sec_zone,phase,cid,reg,LZ,size=[parms[i] for i in range(len(parms))]
        print(datastore,app,paas_name,sec_zone,phase,cid,reg,LZ,size,sep='\n')

        #calling the repo to fetch the hosts
        ### generating the datastore-file 
        if datastore=='Elasticsearch':
            hosts=self.get_ELK_Hosts(phase,cid,reg)
            ElkDatastoreGenerator().datastoreGenerator(hosts,app,paas_name,sec_zone,phase,cid,reg,LZ,size)
            ElasticsearchExporterGenerator().elasticsearchExporterGenerator(datastore,app,paas_name,sec_zone,phase,cid,reg,LZ)
        elif datastore=='Mongodb':
            hosts,vars,ops_url=self.get_MONGO_Hosts_and_Vars(app,phase,cid,reg,LZ)
            MongoDatastoreGenerator().datastoreGenerator(hosts,vars,ops_url,phase,cid,reg,LZ)
            MongoDBExporterGenerator().mongodbExporterGenerator(datastore,app,paas_name,sec_zone,phase,cid,reg,LZ)
        else:
            hosts,vars,k8s=self.get_Couchbase_Hosts_and_Vars(app,phase,cid,reg,LZ)
            CouchbaseDatastoreGenerator().datastoreGenerator(hosts,vars,size,k8s,phase,cid,reg,LZ)
            CouchbaseExporterGenerator().couchbaseExporterGenerator(datastore,app,paas_name,sec_zone,phase,cid,reg,LZ)
        # print(*hosts,sep='\n')

  
        
       

        ##generating Exporter files

        # ExporterGenerator().exporterGenerator(datastore,app,paas_name,sec_zone,phase,cid,reg,LZ)
        ACNGenerator().acnGenerator(datastore,app,paas_name,sec_zone,phase,cid,reg,LZ,size)


        print("all resources got created for ",reg,'-',phase,'-', cid," in ",paas_name,sep='')