# def refernce_constants():

    
#     file_paths = {
#         'cb_exporter_ref_file_path': 'nosql-paas-inventory/reference/couchbase-exporter/@namespace@-@region@-@phase@-@exporterId@.yaml',
#         'mdb_exporter_ref_file_path': '',
#         'elk_exporter_ref_file_path': '',
#         'cb_acn_ref_file_path': '',
#         'mdb_acn_ref_file_path': '',
#         'quota_ref_file_path': '',
#         'namespace_ref_file_path': ''
#     }
#     return file_paths

cb_exporter_ref_file_path = 'nosql-paas-inventory/reference/couchbase-exporter/@namespace@-@region@-@phase@-@exporterId@.yaml'
mdb_exporter_ref_file_path = 'nosql-paas-inventory/reference/mongodb-exporter/@namespace@-@region@-@phase@-@exporterId@.yaml'
elk_exporter_ref_file_path = 'nosql-paas-inventory/reference/elasticsearch-exporter/@namespace@-@region@-@phase@-@exporterId@.yaml'

acn_ref_file_path = 'nosql-paas-inventory/reference/acn/datastore-@datastore@-acn-@app@-@phase@-@app@.yaml'
acns_ref_file_path = 'nosql-paas-inventory/reference/acn-services/datastore-@datastore@-acn-@app@-@phase@-@app@.yaml'


quota_ref_file_path = 'nosql-paas-inventory/reference/quota/dbaas-@datastore@.yaml'
namespace_ref_file_path = 'nosql-paas-inventory/reference/namespace/datastore-@datastore@-@type@-@app@.yaml'