#!/usr/bin/env python3
#Check HPE 3PAR drives state

import sys
from optparse import OptionParser
from hpe3parclient import ssh
import pprint

usage = "usage: %prog --ip ip_address"
parser = OptionParser(usage=usage)
parser.add_option("--ip", action="store", type="string", dest="ip_address", help="IP address")
(options, args) = parser.parse_args()

ip_address = options.ip_address

username = 'nagios'
password = 'password'
ssh_client = ssh.HPE3PARSSHClient(ip_address, username, password)

ssh_client.open()

#ssh_client.set_debug_flag(True)
cmd = ['showpd', '-showcols', 'CagePos,State']
results = ssh_client.run(cmd)
ssh_client.close()

problem_bool = False
message = ''
count_disks = 0

for index, line in enumerate(results):
   if index == 0:
      headers = line.split(',')
   else:
      split = line.split(',')
      member = {}
      count_disks += 1
      exception = False
      for i, header in enumerate(headers):
         try:
            member[header] = split[i]
         except IndexError:
            exception = True
      if exception == False and (member['State'] == 'failed' or member['State'] == 'degraded'):
         message += 'Disk '+member['CagePos']+' FAILED '
         problem_bool = True

if problem_bool == False:
        count_disks -= 2
        print('OK - All the '+str(count_disks)+' disks are in NORMAL operation')
        sys.exit(0)
elif problem_bool == True:
        print('CRITICAL - '+message)
        sys.exit(2)


