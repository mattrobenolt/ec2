from .base import RUNNING_STATE
from boto.ec2.instance import Instance
from mock import patch
import unittest
import re

import ec2


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
