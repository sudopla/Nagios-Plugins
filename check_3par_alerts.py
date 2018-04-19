#!/usr/bin/env python3
#Check HPE 3PAR health

import sys
from optparse import OptionParser
from hpe3parclient import ssh
import re

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
cmd = ['showalert', '-oneline']
results = ssh_client.run(cmd)
ssh_client.close()

problem_bool = False
message = ''

for index, line in enumerate(results):
   if index == 0:
      headers = line.split(',')
      for n, header in enumerate(headers):
         headers[n] = re.sub('-', '', header)
   else:
      split = line.split(',')
      member = {}
      exception = False
      for i, header in enumerate(headers):
         try:
            member[header] = split[i]
         except IndexError:
            exception = True
      if exception == False and member['Severity'] == 'Major' and member['Type'] == 'Component state change':
         message += member['Message']
         problem_bool = True

if problem_bool == False:
        print('OK - State: Normal ')
        sys.exit(0)
elif problem_bool == True:
        print('CRITICAL - General State: DEGRADED -'+message)
        sys.exit(2)


