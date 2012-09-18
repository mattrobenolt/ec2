from __future__ import with_statement

from boto.ec2.instance import Instance
from unittest import TestCase
from mock import MagicMock, patch
import re

import ec2


class InstancesTestCase(TestCase):
    def _patch_connection(self):
        return patch('ec2.types.get_connection', return_value=self.connection)

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
            i1.state = 'running'
            i1.tags = {'Name': 'instance-%d' % instance_count}
            instance_count += 1
            i2 = Instance()
            i2.id = 'i-abc%d' % instance_count
            i2.state = 'stopped'
            i2.tags = {'Name': 'instance-%d' % instance_count}
            instance_count += 1
            reservation = MagicMock()
            reservation.instances.__iter__ = MagicMock(return_value=iter([i1, i2]))
            reservations.append(reservation)

        self.connection = MagicMock()
        self.connection.get_all_instances = MagicMock(return_value=reservations)

    def tearDown(self):
        ec2.credentials.ACCESS_KEY_ID = None
        ec2.credentials.SECRET_ACCESS_KEY = None
        ec2.credentials.REGION_NAME = 'us-east-1'

    def test_credentials(self):
        self.assertEquals(dict(**ec2.credentials()), {'aws_access_key_id': 'abc', 'aws_secret_access_key': 'xyz', 'region_name': 'us-east-1'})

    def test_connect(self):
        with patch('boto.ec2.connect_to_region') as mock:
            ec2.connection.get_connection()
            mock.assert_called_once_with(aws_access_key_id='abc', aws_secret_access_key='xyz', region_name='us-east-1')

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


class ComparisonTests(TestCase):
    def setUp(self):
        self.instance = Instance()
        self.instance.state = 'running'
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
