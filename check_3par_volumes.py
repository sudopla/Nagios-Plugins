#!/usr/bin/env python3
#Check HPE 3PAR volumes state

import sys
from optparse import OptionParser
from hpe3parclient import client, exceptions

usage = "usage: %prog --ip ip_address"
parser = OptionParser(usage=usage)

parser.add_option("--ip", action="store", type="string", dest="ip_address", help="IP address")

(options, args) = parser.parse_args()

ip_address = options.ip_address
cl = client.HPE3ParClient('http://'+ip_address+':8008/api/v1')
username = 'nagios'
password = 'password'

try:
   cl.login(username, password)
except:
   print("Login failed.")
   sys.exit(3)

volumes = cl.getVolumes()
cl.logout()

problem_bool = False
message = ''

for volume in volumes['members']:
	if volume['state'] == 2:
		message += 'Volume: '+volume['name']+' is Degraded '
		problem_bool = True
	if volume['state'] == 3:
		message += 'Volume: '+volume['name']+' Failed '
		problem_bool = True

if problem_bool == False:
	print('OK - All the volumes are in NORMAL operation')
	sys.exit(0)
elif problem_bool == True:
	print('CRITICAL - '+message) 
	sys.exit(2)





