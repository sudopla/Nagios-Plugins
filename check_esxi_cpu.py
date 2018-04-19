#!/usr/bin/env python3
#Check CPU Usage on ESXi host

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

max_cpu_GHz = round(host.systemResources.config.cpuAllocation.limit / 1000, 2)
cpu_usage_GHz = round(host.summary.quickStats.overallCpuUsage / 1000, 2)
cpu_usage_percent = round((cpu_usage_GHz / max_cpu_GHz) * 100, 2)

Disconnect(c)

if cpu_usage_percent < 80:
	print('OK - CPU usage at '+str(cpu_usage_percent) +'% - ' + str(cpu_usage_GHz) + 'GHz used of ' + str(max_cpu_GHz) + 'GHz')
	sys.exit(0)
elif cpu_usage_percent >= 80 and cpu_usage_percent < 90:
	print('WARNING - CPU usage at '+str(cpu_usage_percent) +'% - ' + str(cpu_usage_GHz) + 'GHz used of ' + str(max_cpu_GHz) + 'GHz')
	sys.exit(1)
elif cpu_usage_percent >= 90:
	print('CRITICAL - CPU usage at '+str(cpu_usage_percent) +'% -  ' + str(cpu_usage_GHz) + 'GHz used of ' + str(max_cpu_GHz) + 'GHz')
	sys.exit(2)
else:
	print('UNKNOWN value')
	sys.exit(3)

