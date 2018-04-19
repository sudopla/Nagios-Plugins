#!/usr/bin/env python3
#Check disk space on a Linux VM

import sys
from optparse import OptionParser
from pyVim import connect
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl

usage = "usage: %prog --vm_uuid uuid -p partition"
parser = OptionParser(usage=usage)

parser.add_option("--vm_uuid", action="store", type="string", dest="vm_uuid", help="VM UUID")
parser.add_option("-p", "--partition", action="store", type="string", dest="partition", help="Partition letter E or path")

(options, args) = parser.parse_args()


s = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
s.verify_mode = ssl.CERT_NONE

c = SmartConnect(host="IP", user="nagios@vsphere.local", pwd="password", sslContext=s)

content = c.RetrieveContent()

#vm_uuid = '5032ea24-02c5-f1ba-6ca5-05d08d2ff8cc'
vm_uuid = options.vm_uuid
partition = options.partition
search_index = content.searchIndex
# quick/dirty way to find an ESXi host
vm = search_index.FindByUuid(uuid=vm_uuid, vmSearch=True, instanceUuid=True)

disk_found = False

if (vm.guest.toolsRunningStatus == 'guestToolsRunning'):
	disks = vm.guest.disk
	for disk in disks:
		disk_name = disk.diskPath
		if disk_name == partition:
			capacity = disk.capacity
			free_space = disk.freeSpace
			capacity_GB = round(((capacity / 1024) / 1024) / 1024, 2)
			free_space_GB = round(((free_space / 1024) / 1024) / 1024, 2)
			used_space_GB = round(capacity_GB - free_space_GB)
			used_space_percent = round((used_space_GB / capacity_GB) * 100, 2)
			#Close connection first
			Disconnect(c)
			if used_space_percent < 90:
				print('OK - ' + disk_name + ' usage at ' + str(used_space_percent) + '% with ' + str(free_space_GB)+'GB free of ' + str(capacity_GB) + 'GB')
				sys.exit(0)
			elif used_space_percent >= 90 and used_space_percent < 95:
				print('WARNING - ' + disk_name + ' usage at ' + str(used_space_percent) + '% with ' + str(free_space_GB)+'GB free of ' + str(capacity_GB) + 'GB')
				sys.exit(1)
			elif used_space_percent >= 95:
				print('CRITICAL - ' + disk_name + ' usage at ' + str(used_space_percent) + '% with ' + str(free_space_GB)+'GB free of ' + str(capacity_GB) + 'GB')
				sys.exit(2)
			disk_found = True

#Close connection in case vm does not have VMware tools installed or could not find disk path
Disconnect(c)

#if it could not find the drive
if disk_found != True:
	print('UNKNOWN value - VMware Tools Not Running')
	sys.exit(3)




