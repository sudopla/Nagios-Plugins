#!/usr/bin/env python3
#Check HPE 3PAR available space

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

system_info = cl.getStorageSystemInfo()
cl.logout()

capacity_TB = round((system_info['totalCapacityMiB'] / 1024) / 1024, 2)
free_space_TB = round((system_info['freeCapacityMiB'] / 1024) / 1024, 2)
used_space_TB = round( (system_info['allocatedCapacityMiB'] / 1024) / 1024, 2)
used_space_percent = round((used_space_TB / capacity_TB) * 100, 2)

#Close connection first
if used_space_percent < 90:
	print('OK - HPE 3PAR usage at ' + str(used_space_percent) + '% with ' + str(free_space_TB)+'TB free of ' + str(capacity_TB) + 'TB')
	sys.exit(0)
elif used_space_percent >= 90 and used_space_percent < 95:
	print('WARNING - HPE 3PAR usage at ' + str(used_space_percent) + '% with ' + str(free_space_TB)+'TB free of ' + str(capacity_TB) + 'TB')
	sys.exit(1)
elif used_space_percent >= 95:
	print('CRITICAL - HPE 3PAR usage at ' + str(used_space_percent) + '% with ' + str(free_space_TB)+'TB free of ' + str(capacity_TB) + 'TB')
	sys.exit(2)





