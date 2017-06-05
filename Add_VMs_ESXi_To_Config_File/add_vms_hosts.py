#!/usr/bin/env python3

from pyVim.connect import SmartConnectNoSSL, Disconnect

import atexit
import os
import re

c = SmartConnectNoSSL(host="vCenter_IP_ADD", user="username", pwd="password")

atexit.register(Disconnect, c)

#Remove configuration files
cfg_path = '/etc/nagios3/conf.d/vmware.cfg'
if os.path.exists(cfg_path):
	os.remove(cfg_path)

content = c.RetrieveContent()
datacenters = content.rootFolder.childEntity
for datacenter in datacenters:  #Iterate through DataCenters
	print ('Data Center: ' + datacenter.name)
	clusters =  datacenter.hostFolder.childEntity
	for cluster in clusters:  #Iterate through the clusters in DC
		print ('Cluster: ' + cluster.name)
		hosts = cluster.host
		for host in hosts:  #Iterate through Hosts in the cluster
			print ('Host: ' + host.name)
			ip_address = host.summary.managementServerIp  	       		
			with open('/etc/nagios3/conf.d/vmware.cfg', 'a') as cfg:
				cfg.write('define host{\nuse generic-host\nhost_name '+host.name+'\nalias '+host.name+'\naddress '+ip_address+'\n}\n')
			vms = host.vm
			for vm in vms:
				print ('VM: ' + vm.name)
				if vm.summary.guest is not None:
					ip_address = vm.summary.guest.ipAddress
					if ip_address:
						print('IP: '+ ip_address)
						vm_name = vm.name.replace('&', '')
						vm_name = vm_name.replace(' ', '_')
						with open('/etc/nagios3/conf.d/vmware.cfg', 'a') as cfg:
							cfg.write('define host{\nuse generic-host\nhost_name '+vm_name+'\nalias '+vm_name+'\naddress '+ip_address+'\n}\n')
