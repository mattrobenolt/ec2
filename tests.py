from __future__ import with_statement

from boto.ec2.instance import Instance, InstanceState
from boto.ec2.securitygroup import SecurityGroup
from boto.vpc.vpc import VPC
from mock import MagicMock, patch
import unittest
import re

import ec2

RUNNING_STATE = InstanceState(16, 'running')
STOPPED_STATE = InstanceState(64, 'stopped')


class InstancesTestCase(unittest.TestCase):
    def _patch_connection(self):
        return patch('ec2.types.get_connection', return_value=self.connection)

    def _patch_vpc_connection(self):
        return patch('ec2.types.get_vpc_connection', return_value=self.vpc_connection)

    def setUp(self):
        ec2.credentials.ACCESS_KEY_ID = 'abc'
        ec2.credentials.SECRET_ACCESS_KEY = 'xyz'

        # Build up two reservations, with two instances each, totalling 4 instances
        # Two running, two stopped
        reservations = []
        instance_count = 0
        for i in xrange(2):
            i1 = Instance()
            i1.id = 'i-abc%d' % instance_count
            i1._state = RUNNING_STATE
            i1.tags = {'Name': 'instance-%d' % instance_count}
            instance_count += 1
            i2 = Instance()
            i2.id = 'i-abc%d' % instance_count
            i2._state = STOPPED_STATE
            i2.tags = {'Name': 'instance-%d' % instance_count}
            instance_count += 1
            reservation = MagicMock()
            reservation.instances.__iter__ = MagicMock(return_value=iter([i1, i2]))
            reservations.append(reservation)

        security_groups = []
        for i in xrange(2):
            sg = SecurityGroup()
            sg.id = 'sg-abc%d' % i
            sg.name = 'group-%d' % i
            sg.description = 'Group %d' % i
            security_groups.append(sg)

        vpcs = []
        for i in xrange(2):
            vpc = VPC()
            vpc.id = 'vpc-abc%d' % i
            if i % 2:
                vpc.state = 'pending'
                vpc.is_default = False
                vpc.instance_tenancy = 'default'
            else:
                vpc.state = 'available'
                vpc.is_default = True
                vpc.instance_tenancy = 'dedicated'
            vpc.cidr_block = '10.%d.0.0/16' % i
            vpc.dhcp_options_id = 'dopt-abc%d' % i
            vpcs.append(vpc)

        self.connection = MagicMock()
        self.connection.get_all_instances = MagicMock(return_value=reservations)
        self.connection.get_all_security_groups = MagicMock(return_value=security_groups)

        self.vpc_connection = MagicMock()
        self.vpc_connection.get_all_vpcs = MagicMock(return_value=vpcs)

    def tearDown(self):
        ec2.credentials.ACCESS_KEY_ID = None
        ec2.credentials.SECRET_ACCESS_KEY = None
        ec2.credentials.REGION_NAME = 'us-east-1'
        ec2.instances.clear()
        ec2.security_groups.clear()

    def test_credentials(self):
        self.assertEquals(dict(**ec2.credentials()), {'aws_access_key_id': 'abc', 'aws_secret_access_key': 'xyz', 'region_name': 'us-east-1'})

    def test_connect(self):
        with patch('boto.ec2.connect_to_region') as mock:
            ec2.connection.get_connection()
            mock.assert_called_once_with(aws_access_key_id='abc', aws_secret_access_key='xyz', region_name='us-east-1')

        with patch('boto.vpc.connect_to_region') as mock:
            ec2.connection.get_vpc_connection()
            mock.assert_called_once_with(aws_access_key_id='abc', aws_secret_access_key='xyz', region_name='us-east-1')

    def test_instances_all(self):
        "instances.all() should iterate over all reservations and collect all instances, then cache the results"
        with self._patch_connection() as mock:
            instances = ec2.instances.all()
            self.assertEquals(4, len(instances))
            # all() should cache the connection and list of instances
            # so when calling a second time, _connect() shouldn't
            # be called
            ec2.instances.all()
            mock.assert_called_once()  # Should only be called once from the initial _connect

    def test_security_groups_all(self):
        with self._patch_connection() as mock:
            groups = ec2.security_groups.all()
            self.assertEquals(2, len(groups))
            # all() should cache the connection and list of instances
            # so when calling a second time, _connect() shouldn't
            # be called
            ec2.security_groups.all()
            mock.assert_called_once()

    def test_vpcs_all(self):
        with self._patch_vpc_connection() as mock:
            vpcs = ec2.vpcs.all()
            self.assertEquals(2, len(vpcs))
            ec2.vpcs.all()
            mock.assert_called_once()

    def test_instances_filters_integration(self):
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

    def test_security_groups_filters_integration(self):
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

    def test_vpc_filters_integration(self):
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

    def test_instances_get_raises(self):
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

    def test_instances_get(self):
        with self._patch_connection():
            self.assertEquals(ec2.instances.get(id='i-abc0').id, 'i-abc0')

    def test_security_groups_get_raises(self):
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

    def test_security_groups_get(self):
        with self._patch_connection():
            self.assertEquals(ec2.security_groups.get(id='sg-abc0').id, 'sg-abc0')

    def test_vpcs_get_raises(self):
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


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.instance = Instance()
        self.instance._state = RUNNING_STATE
        self.instance.id = 'i-abc'
        self.instance.tags = {'Name': 'awesome'}

    def test_comp(self):
        i = self.instance

        self.assertRaises(AttributeError, ec2.helpers.make_compare, 'state__nope', 'running', i)

        with patch('ec2.helpers.Compare.exact') as mock:
            ec2.helpers.make_compare('state', 'running', i)
            mock.assert_called_once_with('state', 'running', i)

        with patch('ec2.helpers.Compare.exact') as mock:
            ec2.helpers.make_compare('state__exact', 'running', i)
            mock.assert_called_once_with('state', 'running', i)

        with patch('ec2.helpers.Compare.iexact') as mock:
            ec2.helpers.make_compare('state__iexact', 'running', i)
            mock.assert_called_once_with('state', 'running', i)

        with patch('ec2.helpers.Compare.like') as mock:
            ec2.helpers.make_compare('state__like', 'running', i)
            mock.assert_called_once_with('state', 'running', i)

        with patch('ec2.helpers.Compare.regex') as mock:
            ec2.helpers.make_compare('state__regex', 'running', i)
            mock.assert_called_once_with('state', 'running', i)

        with patch('ec2.helpers.Compare.ilike') as mock:
            ec2.helpers.make_compare('state__ilike', 'running', i)
            mock.assert_called_once_with('state', 'running', i)

        with patch('ec2.helpers.Compare.iregex') as mock:
            ec2.helpers.make_compare('state__iregex', 'running', i)
            mock.assert_called_once_with('state', 'running', i)

        with patch('ec2.helpers.Compare.contains') as mock:
            ec2.helpers.make_compare('state__contains', 'running', i)
            mock.assert_called_once_with('state', 'running', i)

        with patch('ec2.helpers.Compare.icontains') as mock:
            ec2.helpers.make_compare('state__icontains', 'running', i)
            mock.assert_called_once_with('state', 'running', i)

        with patch('ec2.helpers.Compare.startswith') as mock:
            ec2.helpers.make_compare('state__startswith', 'running', i)
            mock.assert_called_once_with('state', 'running', i)

        with patch('ec2.helpers.Compare.istartswith') as mock:
            ec2.helpers.make_compare('state__istartswith', 'running', i)
            mock.assert_called_once_with('state', 'running', i)

        with patch('ec2.helpers.Compare.endswith') as mock:
            ec2.helpers.make_compare('state__endswith', 'running', i)
            mock.assert_called_once_with('state', 'running', i)

        with patch('ec2.helpers.Compare.iendswith') as mock:
            ec2.helpers.make_compare('state__iendswith', 'running', i)
            mock.assert_called_once_with('state', 'running', i)

        with patch('ec2.helpers.Compare.isnull') as mock:
            ec2.helpers.make_compare('state__isnull', True, i)
            mock.assert_called_once_with('state', True, i)

    def test_exact(self):
        i = self.instance
        self.assertTrue(ec2.helpers.Compare.exact('state', 'running', i))
        self.assertFalse(ec2.helpers.Compare.exact('state', 'notrunning', i))
        self.assertTrue(ec2.helpers.Compare.exact('name', 'awesome', i))
        self.assertFalse(ec2.helpers.Compare.exact('name', 'notawesome', i))

    def test_iexact(self):
        i = self.instance
        self.assertTrue(ec2.helpers.Compare.iexact('state', 'RUNNING', i))
        self.assertFalse(ec2.helpers.Compare.iexact('state', 'NOTRUNNING', i))
        self.assertTrue(ec2.helpers.Compare.iexact('name', 'AWESOME', i))
        self.assertFalse(ec2.helpers.Compare.iexact('name', 'NOTAWESOME', i))

    def test_like(self):
        i = self.instance
        self.assertTrue(ec2.helpers.Compare.like('state', r'^r.+g$', i))
        self.assertTrue(ec2.helpers.Compare.like('state', re.compile(r'^r.+g$'), i))
        self.assertFalse(ec2.helpers.Compare.like('state', r'^n.+g$', i))
        self.assertFalse(ec2.helpers.Compare.like('state', re.compile(r'^n.+g$'), i))
        self.assertTrue(ec2.helpers.Compare.like('name', r'^a.+e$', i))
        self.assertTrue(ec2.helpers.Compare.like('name', re.compile(r'^a.+e$'), i))
        self.assertFalse(ec2.helpers.Compare.like('name', r'^n.+e$', i))
        self.assertFalse(ec2.helpers.Compare.like('name', re.compile(r'^n.+e$'), i))

    def test_regex(self):
        i = self.instance
        self.assertTrue(ec2.helpers.Compare.regex('state', r'^r.+g$', i))
        self.assertTrue(ec2.helpers.Compare.regex('state', re.compile(r'^r.+g$'), i))
        self.assertFalse(ec2.helpers.Compare.regex('state', r'^n.+g$', i))
        self.assertFalse(ec2.helpers.Compare.regex('state', re.compile(r'^n.+g$'), i))
        self.assertTrue(ec2.helpers.Compare.regex('name', r'^a.+e$', i))
        self.assertTrue(ec2.helpers.Compare.regex('name', re.compile(r'^a.+e$'), i))
        self.assertFalse(ec2.helpers.Compare.regex('name', r'^n.+e$', i))
        self.assertFalse(ec2.helpers.Compare.regex('name', re.compile(r'^n.+e$'), i))

    def test_ilike(self):
        i = self.instance
        self.assertTrue(ec2.helpers.Compare.ilike('state', r'^R.+G$', i))
        self.assertFalse(ec2.helpers.Compare.ilike('state', r'^N.+G$', i))
        self.assertTrue(ec2.helpers.Compare.ilike('name', r'^A.+E$', i))
        self.assertFalse(ec2.helpers.Compare.ilike('name', r'^N.+E$', i))

    def test_iregex(self):
        i = self.instance
        self.assertTrue(ec2.helpers.Compare.iregex('state', r'^R.+G$', i))
        self.assertFalse(ec2.helpers.Compare.iregex('state', r'^N.+G$', i))
        self.assertTrue(ec2.helpers.Compare.iregex('name', r'^A.+E$', i))
        self.assertFalse(ec2.helpers.Compare.iregex('name', r'^N.+E$', i))

    def test_contains(self):
        i = self.instance
        self.assertTrue(ec2.helpers.Compare.contains('state', 'unn', i))
        self.assertFalse(ec2.helpers.Compare.contains('state', 'notunn', i))
        self.assertTrue(ec2.helpers.Compare.contains('name', 'wes', i))
        self.assertFalse(ec2.helpers.Compare.contains('name', 'notwes', i))

    def test_icontains(self):
        i = self.instance
        self.assertTrue(ec2.helpers.Compare.icontains('state', 'UNN', i))
        self.assertFalse(ec2.helpers.Compare.icontains('state', 'NOTUNN', i))
        self.assertTrue(ec2.helpers.Compare.icontains('name', 'WES', i))
        self.assertFalse(ec2.helpers.Compare.icontains('name', 'NOTWES', i))

    def test_startswith(self):
        i = self.instance
        self.assertTrue(ec2.helpers.Compare.startswith('state', 'run', i))
        self.assertFalse(ec2.helpers.Compare.startswith('state', 'notrun', i))
        self.assertTrue(ec2.helpers.Compare.startswith('name', 'awe', i))
        self.assertFalse(ec2.helpers.Compare.startswith('name', 'notawe', i))

    def test_istartswith(self):
        i = self.instance
        self.assertTrue(ec2.helpers.Compare.istartswith('state', 'RUN', i))
        self.assertFalse(ec2.helpers.Compare.istartswith('state', 'NOTRUN', i))
        self.assertTrue(ec2.helpers.Compare.istartswith('name', 'AWE', i))
        self.assertFalse(ec2.helpers.Compare.istartswith('name', 'NOTAWE', i))

    def test_endswith(self):
        i = self.instance
        self.assertTrue(ec2.helpers.Compare.endswith('state', 'ing', i))
        self.assertFalse(ec2.helpers.Compare.endswith('state', 'noting', i))
        self.assertTrue(ec2.helpers.Compare.endswith('name', 'some', i))
        self.assertFalse(ec2.helpers.Compare.endswith('name', 'notsome', i))

    def test_iendswith(self):
        i = self.instance
        self.assertTrue(ec2.helpers.Compare.iendswith('state', 'ING', i))
        self.assertFalse(ec2.helpers.Compare.iendswith('state', 'NOTING', i))
        self.assertTrue(ec2.helpers.Compare.iendswith('name', 'SOME', i))
        self.assertFalse(ec2.helpers.Compare.iendswith('name', 'NOTSOME', i))

    def test_isnull(self):
        i = self.instance
        self.assertTrue(ec2.helpers.Compare.isnull('foo', True, i))
        self.assertFalse(ec2.helpers.Compare.isnull('foo', False, i))
        self.assertFalse(ec2.helpers.Compare.isnull('name', True, i))
        self.assertFalse(ec2.helpers.Compare.isnull('name', False, i))

    def test_unknown_key(self):
        i = self.instance
        for attr in ('exact', 'iexact', 'like', 'ilike', 'contains', 'icontains', 'startswith', 'istartswith', 'endswith', 'iendswith'):
            self.assertFalse(getattr(ec2.helpers.Compare, attr)('lol', 'foo', i))


if __name__ == '__main__':
    unittest.main(verbosity=2)
