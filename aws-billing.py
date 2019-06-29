
    
#!/usr/bin/env python3
import argparse
import boto3
import datetime
import csv


parser = argparse.ArgumentParser()
parser.add_argument('--days', type=int, default=30)
args = parser.parse_args()
now = datetime.datetime.utcnow()
start = (now - datetime.timedelta(days=args.days)).strftime('%Y-%m-%d')
end = now.strftime('%Y-%m-%d')
cd = boto3.client('ce', 'us-east-1')
results = []
token = None
while True:
    if token:
        kwargs = {'NextPageToken': token}
    else:
        kwargs = {}
    data = cd.get_cost_and_usage(TimePeriod={'Start': start, 'End':  end}, Granularity='MONTHLY', Metrics=['UnblendedCost'], GroupBy=[{'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'}, {'Type': 'DIMENSION', 'Key': 'SERVICE'}], **kwargs)
    results += data['ResultsByTime']
    token = data.get('NextPageToken')
    if not token:
        break


b_out = open('billing_out.csv', 'a+')
writer = csv.writer(b_out)
writer.writerow(['TimePeriod', 'LinkedAccount', 'Service', 'Amount', 'Unit', 'Estimated'])
for result_by_time in results:
    for group in result_by_time['Groups']:
        amount = group['Metrics']['UnblendedCost']['Amount']
        unit = group['Metrics']['UnblendedCost']['Unit']
        out_list = [result_by_time['TimePeriod']['Start']]
        out_list.extend(group['Keys'])
        out_list.extend([amount, unit, result_by_time['Estimated']])
        writer.writerow(out_list)
b_out.close()




