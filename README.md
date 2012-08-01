# Amazon EC2
Ever try to query for some instances with boto? It sucks.

```python
>>> import ec2
>>> ec2.instances.filter(state='running', name__startswith='production')
[...]
```

## Install
`$ pip install ec2`

## Usage
### AWS credentials
Credentials are defined as a global state, either through an environment variable, or in Python.
```python
ec2.credentials.ACCESS_KEY_ID = 'xxx'
ec2.credentials.SECRET_ACCESS_KEY = 'xxx'
```

## Querying
### All instances
```python
ec2.instances.all()
```

### Filtering
*Filter style is based on Django's ORM*
All filters map directly to instance properties.
```python
ec2.instances.filter(id='i-xxx')  # Exact instance id
ec2.instances.filter(state='running')  # Exact instance state
```

Filters will also dig into tags.
```python
ec2.instances.filter(name='production-web')  # Exact "Name" tag
```

Filters support many types of comparisons, similar to Django's ORM filters.
```python
ec2.instances.filter(name__exact='production-web-01')  # idential to `name='...'`
ec2.instances.filter(name__iexact='PRODUCTION-WEB-01')  # Case insensitive "exact"
ec2.instances.filter(name__like=r'^production-web-\d+$')  # Match against a regular expression
ec2.instances.filter(name__ilike=r'^production-web-\d+$')  # Case insensitive "like"
ec2.instances.filter(name__contains='web')  # Field contains the search string
ec2.instances.filter(name__icontains='WEB')  # Case insensitive "contains"
ec2.instances.filter(name__startswith='production')  # Fields starts with the search string
ec2.instances.filter(name__istartswith='PRODUCTION')  # Case insensitive "startswith"
ec2.instances.filter(name__endswith='01')  # Fields ends with the search string
ec2.instances.filter(name__iendswith='01')  # Case insensitive "endswith"
```

Filters can also be chained.
```python
ec2.instances.filter(state='running', name__startswith='production')
```

### Search fields
 * id *(Instance id)*
 * state *(running, terminated, pending, shutting-down, stopping, stopped)*
 * public_dns_name
 * ip_address
 * private_dns_name
 * private_ip_address
 * root_device_type *(ebs, instance-store)*
 * key_name *(name of the SSH key used on the instance)*
 * image_id *(Id of the AMI)*

All fields can be found at: https://github.com/boto/boto/blob/d91ed8/boto/ec2/instance.py#L157-204

## Example
### Get public ip addresses from all running instances who are named production-web-{number}
```python
import ec2
ec2.credentials.ACCESS_KEY_ID = 'xxx'
ec2.credentials.SECRET_ACCESS_KEY = 'xxx'

for instance in ec2.instances.filter(state='running', name__like=r'^production-web-\d+$'):
    print instance.ip_address
```
