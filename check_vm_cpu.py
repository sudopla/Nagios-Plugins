#!/usr/bin/env python3
#Check VM CPU usage

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


s = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
s.verify_mode = ssl.CERT_NONE

c = SmartConnect(host="IP", user="nagios@vsphere.local", pwd="password", sslContext=s)

content = c.RetrieveContent()

#vm_uuid = '5032ea24-02c5-f1ba-6ca5-05d08d2ff8cc'
vm_uuid = options.vm_uuid
search_index = content.searchIndex
# quick/dirty way to find an ESXi host
vm = search_index.FindByUuid(uuid=vm_uuid, vmSearch=True, instanceUuid=True)


max_cpu_GHz = round(vm.runtime.maxCpuUsage / 1000, 2)
cpu_usage_GHz = round(vm.summary.quickStats.overallCpuUsage / 1000, 2)
cpu_usage_percent = round((cpu_usage_GHz / max_cpu_GHz) * 100, 2)

Disconnect(c)

if cpu_usage_percent < 90:
	print('OK - CPU usage at '+str(cpu_usage_percent) +'% - ' + str(cpu_usage_GHz) + 'GHz used of ' + str(max_cpu_GHz) + 'GHz')
	sys.exit(0)
elif cpu_usage_percent >= 90 and cpu_usage_percent < 95:
	print('WARNING - CPU usage at '+str(cpu_usage_percent) +'% - ' + str(cpu_usage_GHz) + 'GHz used of ' + str(max_cpu_GHz) + 'GHz')
	sys.exit(1)
elif cpu_usage_percent >= 95:
	print('CRITICAL - CPU usage at '+str(cpu_usage_percent) +'% -  ' + str(cpu_usage_GHz) + 'GHz used of ' + str(max_cpu_GHz) + 'GHz')
	sys.exit(2)
else:
	print('UNKNOWN value')
	sys.exit(3)

