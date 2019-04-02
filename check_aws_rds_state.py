#!/usr/bin/env python3
import sys
from optparse import OptionParser
import boto3
from datetime import datetime, timedelta

usage = "usage: %prog --name rds_instance_name"
parser = OptionParser(usage=usage)

parser.add_option("--name", "--rds_name", action="store", type="string", dest="rds_name", help="Name of RDS Instance")

(options, args) = parser.parse_args()
rds_name = options.rds_name

try:
   session = boto3.session.Session(
       aws_access_key_id='',
       aws_secret_access_key='',
       region_name='us-east-1'
   )
except:
   print("Login failed.")
   sys.exit(3)

# Get Total Assigned Storage to RDS instance
rds_client = session.client('rds')
rds_instance = rds_client.describe_db_instances(DBInstanceIdentifier=rds_name)

db_status = rds_instance['DBInstances'][0]['DBInstanceStatus']

if db_status in {'failed', 'inaccessible-encryption-credentials', 'stopped', 'storage-full'}:
   print('CRITICAL - General State: '+db_satus)
   sys.exit(2)
else:
   print('OK - State: '+db_status)
   sys.exit(0)



