#!/usr/bin/env python3

import sys
from optparse import OptionParser
import requests, json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

usage = "usage: %prog --ip ip_address"
parser = OptionParser(usage=usage)
parser.add_option("--ip", action="store", type="string", dest="ip_address", help="IP address")
(options, args) = parser.parse_args()

ip_address = options.ip_address

api_root = 'https://'+ip_address+'/irisservices/api/v1'

creds = json.dumps({"domain": "LOCAL", "username": "username", "password": "password"})
url = api_root + '/public/accessTokens'
HEADER = {'accept': 'application/json', 'content-type': 'application/json'}

response = requests.post(url, data=creds, headers=HEADER, verify=False)

problem_bool = False
message = ''

if response.status_code == 201:
   accessToken = response.json()['accessToken']
   tokenType = response.json()['tokenType']
   HEADER = {'accept': 'application/json', \
             'content-type': 'application/json', \
             'authorization': tokenType + ' ' + accessToken}

   url_statistics = api_root + '/public/alerts?alertStateList=kOpen&alertSeverityList=kCritical&alertCategoryList=kDisk&alertCategoryList=kNode&alertCategoryList=kCluster&alertCategoryList=kNodeHealth&alertCategoryList=kClusterHealth'

   response = requests.get(url_statistics, headers=HEADER, verify=False)

   alerts = response.json()
   count = 0
   if alerts:
      problem_bool = True
      for alert in alerts:
         alert_name = alert['alertDocument']['alertName']
         alert_description = alert['alertDocument']['alertDescription']
         message += alert_name +'-'+alert_description+' '
      
else:
   print("Login failed.")
   sys.exit(3)

if problem_bool == False:
        print('OK - State: Normal ')
        sys.exit(0)
elif problem_bool == True:
        print('CRITICAL - General State: DEGRADED - '+message)
        sys.exit(2)



