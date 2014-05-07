from .base import BaseTestCase
from mock import patch

import ec2


class ConnectionTestCase(BaseTestCase):
    def test_connect(self):
        with patch('boto.ec2.connect_to_region') as mock:
            ec2.connection.get_connection()
            mock.assert_called_once_with(aws_access_key_id='abc', aws_secret_access_key='xyz', region_name='us-east-1')

        with patch('boto.vpc.connect_to_region') as mock:
            ec2.connection.get_vpc_connection()
            mock.assert_called_once_with(aws_access_key_id='abc', aws_secret_access_key='xyz', region_name='us-east-1')


class CredentialsTestCase(BaseTestCase):
    def test_credentials(self):
        self.assertEquals(dict(**ec2.credentials()), {'aws_access_key_id': 'abc', 'aws_secret_access_key': 'xyz', 'region_name': 'us-east-1'})
