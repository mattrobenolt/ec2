import ec2

ec2.credentials.ACCESS_KEY_ID = 'xxx'
ec2.credentials.SECRET_ACCESS_KEY = 'xxx'
ec2.credentials.REGION_NAME = 'us-west-2'
# ec2.credentials.from_file('credentials.csv')

print ec2.instances.all()
for i in ec2.instances.filter(state__iexact='rUnning', name__endswith='01', name__startswith='production'):
    print i.tags['Name']
print ec2.instances.filter(id__iregex=r'^I\-')
