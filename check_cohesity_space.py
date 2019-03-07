#!/usr/bin/env python3
import sys
from optparse import OptionParser
import requests, json

#Supress InsecureRequestWarning warning from output
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

usage = "usage: %prog --ip ip_address"
parser = OptionParser(usage=usage)

parser.add_option("--ip", action="store", type="string", dest="ip_address", help="IP address")

(options, args) = parser.parse_args()

ip_address = options.ip_address

#Log in and get token
api_root = 'https://'+ip_address+'/irisservices/api/v1'
creds = json.dumps({"domain": "LOCAL", "username": " username", "password": "password"})
url = api_root + '/public/accessTokens'
HEADER = {'accept': 'application/json', 'content-type': 'application/json'}

response = requests.post(url, data=creds, headers=HEADER, verify=False)

if response.status_code == 201:
   accessToken = response.json()['accessToken']
   tokenType = response.json()['tokenType']
   HEADER = {'accept': 'application/json', \
             'content-type': 'application/json', \
             'authorization': tokenType + ' ' + accessToken}
else:
   print("Login failed.")
   sys.exit(3)

#Get storage values
url_statistics = api_root + '/public/cluster?fetchStats=True'

response = requests.get(url_statistics, headers=HEADER, verify=False)

perfStats = response.json()['stats']['usagePerfStats']
total_capacity_bytes = perfStats['physicalCapacityBytes']
used_space_bytes = perfStats['totalPhysicalUsageBytes']

capacity_TB = round((((total_capacity_bytes / 1024) / 1024) / 1024) / 1024 , 2)
used_space_TB = round((((used_space_bytes / 1024) / 1024) / 1024) / 1024 , 2)
free_space_TB = round(capacity_TB - used_space_TB, 2)
used_space_percent = round((used_space_TB / capacity_TB) * 100, 2)

#Close connection first
if used_space_percent < 90:
	print('OK - Cohesity usage at ' + str(used_space_percent) + '% with ' + str(free_space_TB)+'TB free of ' + str(capacity_TB) + 'TB', end='')
	print(' | space_usage='+str(used_space_TB)+';;;0;'+str(capacity_TB))
	sys.exit(0)
elif used_space_percent >= 90 and used_space_percent < 95:
	print('WARNING - Cohesity usage at ' + str(used_space_percent) + '% with ' + str(free_space_TB)+'TB free of ' + str(capacity_TB) + 'TB', end='')
	print(' | space_usage='+str(used_space_TB)+';;;0;'+str(capacity_TB))
	sys.exit(1)
elif used_space_percent >= 95:
	print('CRITICAL - Cohesity usage at ' + str(used_space_percent) + '% with ' + str(free_space_TB)+'TB free of ' + str(capacity_TB) + 'TB', end='')
	print(' | space_usage='+str(used_space_TB)+';;;0;'+str(capacity_TB))
	sys.exit(2)






