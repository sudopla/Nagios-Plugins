#!/usr/bin/env python3
#Check VM Memory Usage

import sys
from optparse import OptionParser
from pyVim import connect
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl

usage = "usage: %prog --vm_uuid uuid"
parser = OptionParser(usage=usage)

parser.add_option("--vm_uuid", action="store", type="string", dest="vm_uuid", help="VM UUID")

(options, args) = parser.parse_args()


#s = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
#s.verify_mode = ssl.CERT_NONE
s = ssl._create_unverified_context()

c = SmartConnect(host="IP", user="nagios@vsphere.local", pwd="password", sslContext=s)

content = c.RetrieveContent()

#vm_uuid = '5032ea24-02c5-f1ba-6ca5-05d08d2ff8cc'
vm_uuid = options.vm_uuid
search_index = content.searchIndex
# quick way to find a VM
vm = search_index.FindByUuid(uuid=vm_uuid, vmSearch=True, instanceUuid=True)


max_memory_GB = round(vm.runtime.maxMemoryUsage / 1024)
mem_active_used_GB = round(vm.summary.quickStats.guestMemoryUsage / 1024, 2)
mem_active_free_GB = max_memory_GB - mem_active_used_GB
memory_active_percent = round((mem_active_used_GB / max_memory_GB) * 100, 2)

Disconnect(c)

if memory_active_percent < 90:
	print('OK - Active memory at '+ str(memory_active_percent) +'% - ' + str(mem_active_used_GB) + 'GB of ' + str(max_memory_GB) + 'GB used')
	sys.exit(0)
elif memory_active_percent >= 90 and memory_active_percent < 95:
	print('WARNING - Active memory at '+ str(memory_active_percent) +'% - ' + str(mem_active_used_GB) + 'GB of ' + str(max_memory_GB) + 'GB used')
	sys.exit(1)
elif memory_active_percent >= 95:
	print('CRITICAL - Active memory at '+ str(memory_active_percent) +'% - ' + str(mem_active_used_GB) + 'GB of ' + str(max_memory_GB) + 'GB used')
	sys.exit(2)
else:
	print('UNKNOWN value')
	sys.exit(3)

