#!/usr/bin/env python3
#Check Memory on ESXi host

import sys
from optparse import OptionParser
from pyVim import connect
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl

usage = "usage: %prog --host_name host_name"
parser = OptionParser(usage=usage)

parser.add_option("--host_name", action="store", type="string", dest="host_name", help="Host Name")

(options, args) = parser.parse_args()


s = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
s.verify_mode = ssl.CERT_NONE

c = SmartConnect(host="IP", user="nagios@vsphere.local", pwd="password", sslContext=s)

content = c.RetrieveContent()

host_name = options.host_name
search_index = content.searchIndex
# quick/dirty way to find an ESXi host
host = search_index.FindByDnsName(dnsName=host_name, vmSearch=False)

max_memory_GB = round(host.systemResources.config.memoryAllocation.limit / 1024)
mem_active_used_GB = round(host.summary.quickStats.overallMemoryUsage / 1024, 2)
mem_active_free_GB = max_memory_GB - mem_active_used_GB
memory_active_percent = round((mem_active_used_GB / max_memory_GB) * 100, 2)

Disconnect(c)

if memory_active_percent < 80:
	print('OK - Active memory at '+ str(memory_active_percent) +'% - ' + str(mem_active_used_GB) + 'GB of ' + str(max_memory_GB) + 'GB used')
	sys.exit(0)
elif memory_active_percent >= 80 and memory_active_percent < 90:
	print('WARNING - Active memory at '+ str(memory_active_percent) +'% - ' + str(mem_active_used_GB) + 'GB of ' + str(max_memory_GB) + 'GB used')
	sys.exit(1)
elif memory_active_percent >= 90:
	print('CRITICAL - Active memory at '+ str(memory_active_percent) +'% - ' + str(mem_active_used_GB) + 'GB of ' + str(max_memory_GB) + 'GB used')
	sys.exit(2)
else:
	print('UNKNOWN value')
	sys.exit(3)

