#!/usr/bin/python


import sys
import json
import fileinput
from argparse import ArgumentParser
from jinja2 import Template, Environment, FileSystemLoader

#Generate rules.toml updating the backends configuration
global_tenants = []
global_frontends = []

def read_azurerm():
	azure_json_str = ""
	for line in sys.stdin:
		azure_json_str += line

	return json.loads(azure_json_str)

def get_tenant_by_name(tenant_name):
	for t in global_tenants:
		if t['tenant'] == tenant_name:
			return t

	#print('create tenant {0}'.format(tenant_name))
	new_tenant = {}
	new_tenant['tenant']=tenant_name
	new_tenant['backends']=[]
	global_tenants.append(new_tenant)
	return new_tenant

	

def get_backend_by_name(tenant, backend_name, port=443):
	for b in tenant['backends']:
		if b['name'] == backend_name:
			return b

	#print('create backend {0}'.format(backend_name))
	new_backend = {}
	new_backend['name']=backend_name
	new_backend['port']=port
	new_backend['servers']=[]
	tenant['backends'].append(new_backend)
	return new_backend

	
def get_frontend_by_name(tenant_name, frontend_name, backend_name, bind_port):
	for f in global_frontends:
		if f['name'] == frontend_name:
			return f

	#print('create frontend {0}'.format(frontend_name))
	new_frontend = {}
	new_frontend['name']=frontend_name
	new_frontend['tenant_name']=tenant_name
	new_frontend['backend_name']=backend_name
	new_frontend['bind']=bind_port
	new_frontend['dns']=[]
	global_frontends.append(new_frontend)
	return new_frontend

def create_jsondata(azure_vm_json_data, environment, location):

	#look for owner of the VM and add it to the dict
	for jd in azure_vm_json_data:
		#print jd
		if jd['HAPROXY'] == 'false':
			continue
	
		#If the VM belongs to this location we carry on 
		if (jd['Az_Location'] == location) and (jd['ENVIRONMENT'] == environment):
	
			#ensure the backends are populated from tags are populated
			try:
				if jd['TENANT'].strip() and jd['BACKEND'].strip() and jd['PORT'].strip():
					
					#BACKEND INFORMATION
					azure_vm_tenant = jd['TENANT']				
					azure_vm_backend = jd['BACKEND']
					azure_vm_ip = jd['Az_VNicPrivateIPs']
					azure_vm_port = jd['PORT'] if 'PORT' in jd else '443'
					
					#fetch or create a tenant dict
					current_tenant = get_tenant_by_name(azure_vm_tenant)
					#add to new or existing tenant
					current_backend = get_backend_by_name(current_tenant, azure_vm_backend, azure_vm_port)

					#add ip and port to server list
					current_backend['servers'].append("%s:%s" % (azure_vm_ip, azure_vm_port))
			except KeyError, e:
				sys.exit('Failed to KeyError find key: '+ str(e) +'\n'+ str(jd))
				
			#ensure the backends are populated from tags are populated
			try:
				if jd['FRONTEND'].strip() and jd['BIND'].strip() and jd['DNS'].strip():
					
					#grab the attributes that we want from the vm
					azure_vm_frontend = jd['FRONTEND']				
					azure_vm_bind = jd['BIND']				
					azure_vm_dns = jd['DNS']
					
					#fetch or create a frontend dict
					current_frontend = get_frontend_by_name(azure_vm_tenant, azure_vm_frontend, azure_vm_backend, azure_vm_bind)
					current_frontend['dns'].append("%s" % (azure_vm_dns))
			except KeyError, e:
				sys.exit('Failed to KeyError find key: '+ str(e) +'\n'+ str(jd))

				
	return global_tenants, global_frontends

def render_template():
	file_loader = FileSystemLoader("templates")
	env = Environment(loader=file_loader)
	template = env.get_template('haproxy.j2')

	print(template.render(frontends=global_frontends, tenants=global_tenants))

if __name__== "__main__":
	parser = ArgumentParser()
	parser.add_argument("-l", "--location", dest="location", help="parse given location", metavar="LOCATION")
	parser.add_argument("-env", "--environment", dest="environment", help="parse given environment", metavar="ENVIRONMENT")
	args = parser.parse_args()

	azure_vm_json_data = read_azurerm()
	create_jsondata(azure_vm_json_data, args.environment, args.location)
	
	if len(global_frontends) == 0:
		sys.exit('No frontends in this region for env '+ args.environment +' and location '+ args.location)
		
	if len(global_tenants) == 0:
		sys.exit('No tenants/backends in this region for env '+ args.environment +' and location '+ args.location)
	
	#print( global_frontends )
	#print( global_tenants )
	render_template()


