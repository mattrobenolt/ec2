import ec2

ec2.credentials.ACCESS_KEY_ID = 'xxx'
ec2.credentials.SECRET_ACCESS_KEY = 'xxx'

print ec2.instances.all()
for i in ec2.instances.filter(state__iexact='rUnning', name__endswith='01', name__startswith='production'):
    print i.tags['Name']
print ec2.instances.filter(id__iregex=r'^I\-')
