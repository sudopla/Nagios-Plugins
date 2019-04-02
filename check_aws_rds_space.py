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

capacity_GB = rds_instance['DBInstances'][0]['AllocatedStorage']

# Get Free Storage Space
cw_client = session.client('cloudwatch')

result = cw_client.get_metric_statistics(
            Namespace='AWS/RDS',
            MetricName='FreeStorageSpace',
            Dimensions=[{'Name':'DBInstanceIdentifier', 'Value':rds_name}],
            StartTime=datetime.utcnow() - timedelta(seconds=300),
            EndTime=datetime.utcnow(),
            Period=60,
            Statistics=['Average']
)

datapoints = result['Datapoints']
if datapoints:
   if len(datapoints) > 1:
      # Get the last point
      datapoints = sorted(datapoints, key=lambda k: k['Timestamp'])
      datapoints.reverse()

free_space_bytes = datapoints[0]['Average']
free_space_GB = round(((free_space_bytes / 1024) / 1024) / 1024   , 2)
used_space_GB = capacity_GB - free_space_GB

used_space_percent = round((used_space_GB / capacity_GB) * 100, 2)

#Close connection first
if used_space_percent < 90:
	print('OK - RDS space usage at ' + str(used_space_percent) + '% with ' + str(free_space_GB)+'GB free of ' + str(capacity_GB) + 'GB', end='')
	print(' | space_usage='+str(used_space_GB)+';;;0;'+str(capacity_GB))
	sys.exit(0)
elif used_space_percent >= 90 and used_space_percent < 95:
	print('WARNING - RDS space usage at ' + str(used_space_percent) + '% with ' + str(free_space_GB)+'GB free of ' + str(capacity_GB) + 'GB', end='')
	print(' | space_usage='+str(used_space_GB)+';;;0;'+str(capacity_GB))
	sys.exit(1)
elif used_space_percent >= 95:
	print('CRITICAL - RDS space usage at ' + str(used_space_percent) + '% with ' + str(free_space_GB)+'GB free of ' + str(capacity_GB) + 'GB', end='')
	print(' | space_usage='+str(used_space_GB)+';;;0;'+str(capacity_GB))
	sys.exit(2)



