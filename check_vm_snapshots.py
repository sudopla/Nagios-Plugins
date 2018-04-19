#!/usr/bin/env python3
#Nagios plugin to check if a VM has Snapshots and if so, how much space they are using. 

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

snapshot_size_bytes = 0
number_snapshots = 0

if vm.snapshot:
   snapshot_size_bytes = 0
   disk_list = vm.layoutEx.file
   number_snapshots = len(vm.layoutEx.snapshot)
   
   for disk in disk_list:
      if 'snapshot' in disk.type:
         snapshot_size_bytes += disk.size
      if 'delta' in disk.name:
         snapshot_size_bytes += disk.size

   snapshot_size_GB = round(((snapshot_size_bytes / 1024) / 1024) / 1024 , 2)
   Disconnect(c)
   if snapshot_size_GB < 300:
      print('WARNING - The VM has '+str(number_snapshots)+' snapshot(s) using '+str(snapshot_size_GB)+'GB of space')   
      sys.exit(1)
   else:
      print('CRITICAL - The VM has '+str(number_snapshots)+' snapshot(s) using '+str(snapshot_size_GB)+'GB of space')   
      sys.exit(2)     

Disconnect(c)
print('OK - The VM does not have any snapshot')
sys.exit(0)




