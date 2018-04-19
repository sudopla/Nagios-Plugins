#!/usr/bin/env python3
#MAIN SCRIPT TO CREATE NAGIOS CONFIGURATION FILES DYNAMICALLY

from pyVim.connect import SmartConnectNoSSL, Disconnect

import atexit
import os
import re

c = SmartConnectNoSSL(host="vCenter_IP", user="nagios@vsphere.local", pwd="password")

atexit.register(Disconnect, c)

#Remove configuration files
cfg_path = '/etc/nagios3/conf.d/vmware.cfg'
if os.path.exists(cfg_path):
	os.remove(cfg_path)

cfg_services_path = '/etc/nagios3/conf.d/vmware_services.cfg'
if os.path.exists(cfg_services_path):
        os.remove(cfg_services_path)

cfg_esxi_services_path = '/etc/nagios3/conf.d/vmware_esxi_services.cfg'
if os.path.exists(cfg_esxi_services_path):
        os.remove(cfg_esxi_services_path)

cfg_storage_path = '/etc/nagios3/conf.d/vmware_storage.cfg'
if os.path.exists(cfg_storage_path):
        os.remove(cfg_storage_path)

content = c.RetrieveContent()
datacenters = content.rootFolder.childEntity
for datacenter in datacenters:  #Iterate through DataCenters
	print ('Data Center: ' + datacenter.name)
	clusters =  datacenter.hostFolder.childEntity
	for cluster in clusters:  #Iterate through the clusters in DC
		cluster_name = cluster.name
		print ('Cluster: ' + cluster_name)
		hosts = cluster.host
		for host in hosts:  #Iterate through Hosts in the cluster
			host_name = host.name
			print ('Host: ' + host_name)
			# Get ESXi host management IP address
			ip_address = ''
			nic_manager = host.config.virtualNicManagerInfo.netConfig
			for virtual_nic in nic_manager:
				if virtual_nic.nicType == 'management':
					mgmt_nic = virtual_nic.selectedVnic[0]
					for vmkernel in virtual_nic.candidateVnic:
						if vmkernel.key == mgmt_nic:
							ip_address = vmkernel.spec.ip.ipAddress
			with open('/etc/nagios3/conf.d/vmware.cfg', 'a') as cfg:
				cfg.write('define host{\nuse generic-host\nhost_name '+host_name+'\nalias '+host_name+'\naddress '+ip_address+'\nicon_image base/esxi.png\nhostgroups '+cluster_name+'\n}\n')
			vms = host.vm
			for vm in vms:
				print ('VM: ' + vm.name)
				if vm.summary.guest is not None:
					ip_address = vm.summary.guest.ipAddress
					if ip_address:
						print('IP: '+ ip_address)
						vm_name = vm.name.replace('&', '')
						vm_name = vm_name.replace(' ', '_')
						vm_name = vm_name.replace('(', '')
						vm_name = vm_name.replace(')', '')
						
						host_group = cluster_name						
	
						with open('/etc/nagios3/conf.d/vmware.cfg', 'a') as cfg:
							if vm.guest.guestFamily == 'windowsGuest':
								cfg.write('define host{\nuse generic-host\nhost_name '+vm_name+'\nalias '+vm_name+'\naddress '+ip_address+'\nicon_image logos/windows_server.png\nhostgroups '+host_group+'\n}\n')
							elif vm.guest.guestFamily == 'linuxGuest':
								cfg.write('define host{\nuse generic-host\nhost_name '+vm_name+'\nalias '+vm_name+'\naddress '+ip_address+'\nicon_image logos/linux.png\nhostgroups '+host_group+'\n}\n')
							else:
								cfg.write('define host{\nuse generic-host\nhost_name '+vm_name+'\nalias '+vm_name+'\naddress '+ip_address+'\nhostgroups '+host_group+'\n}\n')
						vm_uuid = vm.config.instanceUuid
						with open('/etc/nagios3/conf.d/vmware_services.cfg', 'a') as cfg:
							cfg.write('define service{\nuse generic-service\nhost_name '+vm_name+'\nservice_description CPU\ncheck_command CHECK_CPU!'+vm_uuid+'\n}\n')
							cfg.write('define service{\nuse generic-service\nhost_name '+vm_name+'\nservice_description MEMORY\ncheck_command CHECK_MEMORY!'+vm_uuid+'\n}\n')
							cfg.write('define service{\nuse generic-service\nhost_name '+vm_name+'\nservice_description SNAPSHOTS\ncheck_command CHECK_SNAPSHOTS!'+vm_uuid+'\n}\n')
							disks = vm.guest.disk
							for disk in disks:
								disk_letter = disk.diskPath
								#check if Disk is from Windows or Linux
								if disk_letter[0] != '/':
									cfg.write('define service{\nuse generic-service\nhost_name '+vm_name+'\nservice_description DISK_'+disk_letter[:-2]+'\ncheck_command CHECK_DISK_WIN!'+vm_uuid+'!'+disk_letter[:-2]+'\n}\n')
								else:
									cfg.write('define service{\nuse generic-service\nhost_name '+vm_name+'\nservice_description DISK_'+disk_letter[:-2]+'\ncheck_command CHECK_DISK_LINUX!'+vm_uuid+'!'+disk_letter+'\n}\n')
		
			#ESXi hosts services
			with open('/etc/nagios3/conf.d/vmware_esxi_services.cfg', 'a') as cfg:
				cfg.write('define service{\nuse generic-service\nhost_name '+host_name+'\nservice_description CPU\ncheck_command CHECK_ESXi_CPU!'+host_name+'\n}\n')
				cfg.write('define service{\nuse generic-service\nhost_name '+host_name+'\nservice_description MEMORY\ncheck_command CHECK_ESXi_MEMORY!'+host_name+'\n}\n')

    #DATASTORES
    datastores = cluster.datastore
		host_name = cluster_name+'-Storage'
		for datastore in datastores:
			#Only VMFS Datastores for now
			if datastore.summary.type == 'VMFS':
				datastore_name = datastore.name
				datastore_name = datastore_name.replace(' ', '_')
				datastore_name = datastore_name.replace('(', '')
				datastore_name = datastore_name.replace(')', '')

				datastore_uuid = datastore.info.vmfs.uuid
				with open('/etc/nagios3/conf.d/vmware_storage.cfg', 'a') as cfg:
					cfg.write('define service{\nuse generic-service\nhost_name '+host_name+'\nservice_description '+datastore_name+'\ncheck_command CHECK_DATASTORE!'+datastore_uuid+'!'+cluster.name+'\n}\n')






						


