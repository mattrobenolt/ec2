from .base import BaseTestCase

import ec2


class InstancesTestCase(BaseTestCase):
    def test_all(self):
        "instances.all() should iterate over all reservations and collect all instances, then cache the results"
        with self._patch_connection() as mock:
            instances = ec2.instances.all()
            self.assertEquals(4, len(instances))
            # all() should cache the connection and list of instances
            # so when calling a second time, _connect() shouldn't
            # be called
            ec2.instances.all()
            mock.assert_called_once()  # Should only be called once from the initial _connect

    def test_filters_integration(self):
        with self._patch_connection():
            instances = ec2.instances.filter(state='crap')
            self.assertEquals(0, len(instances))

            instances = ec2.instances.filter(state='running')
            self.assertEquals(2, len(instances))
            self.assertEquals('running', instances[0].state)
            self.assertEquals('running', instances[1].state)

            instances = ec2.instances.filter(state='stopped')
            self.assertEquals(2, len(instances))
            self.assertEquals('stopped', instances[0].state)
            self.assertEquals('stopped', instances[1].state)

            instances = ec2.instances.filter(id__exact='i-abc0')
            self.assertEquals(1, len(instances))

            instances = ec2.instances.filter(id__iexact='I-ABC0')
            self.assertEquals(1, len(instances))

            instances = ec2.instances.filter(id__like=r'^i\-abc\d$')
            self.assertEquals(4, len(instances))

            instances = ec2.instances.filter(id__ilike=r'^I\-ABC\d$')
            self.assertEquals(4, len(instances))

            instances = ec2.instances.filter(id__contains='1')
            self.assertEquals(1, len(instances))

            instances = ec2.instances.filter(id__icontains='ABC')
            self.assertEquals(4, len(instances))

            instances = ec2.instances.filter(id__startswith='i-')
            self.assertEquals(4, len(instances))

            instances = ec2.instances.filter(id__istartswith='I-')
            self.assertEquals(4, len(instances))

            instances = ec2.instances.filter(id__endswith='c0')
            self.assertEquals(1, len(instances))

            instances = ec2.instances.filter(id__iendswith='C0')
            self.assertEquals(1, len(instances))

            instances = ec2.instances.filter(id__startswith='i-', name__endswith='-0')
            self.assertEquals(1, len(instances))

            instances = ec2.instances.filter(id__isnull=False)
            self.assertEquals(4, len(instances))

            instances = ec2.instances.filter(id__isnull=True)
            self.assertEquals(0, len(instances))

    def test_get_raises(self):
        with self._patch_connection():
            self.assertRaises(
                ec2.instances.MultipleObjectsReturned,
                ec2.instances.get,
                id__startswith='i'
            )

            self.assertRaises(
                ec2.instances.DoesNotExist,
                ec2.instances.get,
                name='crap'
            )

    def test_get(self):
        with self._patch_connection():
            self.assertEquals(ec2.instances.get(id='i-abc0').id, 'i-abc0')


class SecurityGroupsTestCase(BaseTestCase):
    def test_all(self):
        with self._patch_connection() as mock:
            groups = ec2.security_groups.all()
            self.assertEquals(2, len(groups))
            # all() should cache the connection and list of instances
            # so when calling a second time, _connect() shouldn't
            # be called
            ec2.security_groups.all()
            mock.assert_called_once()

    def test_filters_integration(self):
        with self._patch_connection():
            groups = ec2.security_groups.filter(name='crap')
            self.assertEquals(0, len(groups))

            groups = ec2.security_groups.filter(id__exact='sg-abc0')
            self.assertEquals(1, len(groups))

            groups = ec2.security_groups.filter(id__iexact='SG-ABC0')
            self.assertEquals(1, len(groups))

            groups = ec2.security_groups.filter(id__like=r'^sg\-abc\d$')
            self.assertEquals(2, len(groups))

            groups = ec2.security_groups.filter(id__ilike=r'^SG\-ABC\d$')
            self.assertEquals(2, len(groups))

            groups = ec2.security_groups.filter(id__contains='1')
            self.assertEquals(1, len(groups))

            groups = ec2.security_groups.filter(id__icontains='ABC')
            self.assertEquals(2, len(groups))

            groups = ec2.security_groups.filter(id__startswith='sg-')
            self.assertEquals(2, len(groups))

            groups = ec2.security_groups.filter(id__istartswith='SG-')
            self.assertEquals(2, len(groups))

            groups = ec2.security_groups.filter(id__endswith='c0')
            self.assertEquals(1, len(groups))

            groups = ec2.security_groups.filter(id__iendswith='C0')
            self.assertEquals(1, len(groups))

            groups = ec2.security_groups.filter(id__startswith='sg-', name__endswith='-0')
            self.assertEquals(1, len(groups))

            groups = ec2.security_groups.filter(id__isnull=False)
            self.assertEquals(2, len(groups))

            groups = ec2.security_groups.filter(id__isnull=True)
            self.assertEquals(0, len(groups))

    def test_get_raises(self):
        with self._patch_connection():
            self.assertRaises(
                ec2.security_groups.MultipleObjectsReturned,
                ec2.security_groups.get,
                id__startswith='sg'
            )

            self.assertRaises(
                ec2.security_groups.DoesNotExist,
                ec2.security_groups.get,
                name='crap'
            )

    def test_get(self):
        with self._patch_connection():
            self.assertEquals(ec2.security_groups.get(id='sg-abc0').id, 'sg-abc0')


class VPCTestCase(BaseTestCase):
    def test_all(self):
        with self._patch_vpc_connection() as mock:
            vpcs = ec2.vpcs.all()
            self.assertEquals(2, len(vpcs))
            ec2.vpcs.all()
            mock.assert_called_once()

    def test_filters_integration(self):
        with self._patch_vpc_connection():
            groups = ec2.vpcs.filter(id__exact='vpc-abc0')
            self.assertEquals(1, len(groups))

            groups = ec2.vpcs.filter(id__iexact='VPC-ABC0')
            self.assertEquals(1, len(groups))

            groups = ec2.vpcs.filter(id__like=r'^vpc\-abc\d$')
            self.assertEquals(2, len(groups))

            groups = ec2.vpcs.filter(id__ilike=r'^VPC\-ABC\d$')
            self.assertEquals(2, len(groups))

            groups = ec2.vpcs.filter(id__contains='1')
            self.assertEquals(1, len(groups))

            groups = ec2.vpcs.filter(id__icontains='ABC')
            self.assertEquals(2, len(groups))

            groups = ec2.vpcs.filter(id__startswith='vpc-')
            self.assertEquals(2, len(groups))

            groups = ec2.vpcs.filter(id__istartswith='vpc-')
            self.assertEquals(2, len(groups))

            groups = ec2.vpcs.filter(id__endswith='c0')
            self.assertEquals(1, len(groups))

            groups = ec2.vpcs.filter(id__iendswith='C0')
            self.assertEquals(1, len(groups))

            groups = ec2.vpcs.filter(id__startswith='vpc-', dhcp_options_id__endswith='abc0')
            self.assertEquals(1, len(groups))

            groups = ec2.vpcs.filter(id__isnull=False)
            self.assertEquals(2, len(groups))

            groups = ec2.vpcs.filter(id__isnull=True)
            self.assertEquals(0, len(groups))

    def test_get_raises(self):
        with self._patch_vpc_connection():
            self.assertRaises(
                ec2.vpcs.MultipleObjectsReturned,
                ec2.vpcs.get,
                id__startswith='vpc'
            )

            self.assertRaises(
                ec2.vpcs.DoesNotExist,
                ec2.vpcs.get,
                name='crap'
            )

    def test_get(self):
        with self._patch_vpc_connection():
            self.assertEquals(ec2.vpcs.get(id='vpc-abc0').id, 'vpc-abc0')
