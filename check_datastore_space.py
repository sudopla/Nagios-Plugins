#!/usr/bin/env python3
#Check datastore space

import sys
from optparse import OptionParser
from pyVim import connect
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl

usage = "usage: %prog --datastore_uuid uuid --cluster_name cluster-name"
parser = OptionParser(usage=usage)

parser.add_option("--datastore_uuid", action="store", type="string", dest="datastore_uuid", help="VM UUID")
parser.add_option("--cluster_name", action="store", type="string", dest="cluster_name", help="Partition letter E or path")

(options, args) = parser.parse_args()

#s = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
#s.verify_mode = ssl.CERT_NONE
s = ssl._create_unverified_context()

c = SmartConnect(host="IP", user="nagios@vsphere.local", pwd="password", sslContext=s)

content = c.RetrieveContent()

datastore_uuid = options.datastore_uuid
cluster_name = options.cluster_name

datacenters = content.rootFolder.childEntity


for datacenter in datacenters:  #Iterate through DataCenters
	clusters =  datacenter.hostFolder.childEntity

	for cluster in clusters:  #Iterate through the clusters in DC
		if cluster.name == cluster_name:
			datastores = cluster.datastore
			for datastore in datastores:
				if datastore.summary.type == 'VMFS':
					if datastore.info.vmfs.uuid == datastore_uuid:
						capacity_bytes = datastore.summary.capacity
						free_space_bytes = datastore.summary.freeSpace
				
						capacity_GB = round(((capacity_bytes / 1024)/ 1024)/ 1024, 2)
						free_space_GB = round(((free_space_bytes / 1024)/ 1024)/ 1024, 2)
						used_space_GB = capacity_GB - free_space_GB
						used_space_percent = round((used_space_GB / capacity_GB) * 100, 2)

					#Close connection first
						Disconnect(c)
						if used_space_percent < 90:
							print('OK - ' + cluster_name + ' usage at ' + str(used_space_percent) + '% with ' + str(free_space_GB)+'GB free of ' + str(capacity_GB) + 'GB')
							sys.exit(0)
						elif used_space_percent >= 90 and used_space_percent < 95:
							print('WARNING - ' + cluster_name + ' usage at ' + str(used_space_percent) + '% with ' + str(free_space_GB)+'GB free of ' + str(capacity_GB) + 'GB')
							sys.exit(1)
						elif used_space_percent >= 95:
							print('CRITICAL - ' + cluster_name + ' usage at ' + str(used_space_percent) + '% with ' + str(free_space_GB)+'GB free of ' + str(capacity_GB) + 'GB')
							sys.exit(2)
						disk_found = True



#Close connection in case vm does not have VMware tools installed or could not find disk path
Disconnect(c)

#if it could not find the drive`
if disk_found != True:
	print('UNKNOWN value')
	sys.exit(3)




