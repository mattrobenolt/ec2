"""
ec2.types
~~~~~~~~~

:copyright: (c) 2014 by Matt Robenolt.
:license: BSD, see LICENSE for more details.
"""

from ec2.connection import get_connection, get_vpc_connection
from ec2.base import objects_base


class instances(objects_base):
    "Singleton to stem off queries for instances"

    @classmethod
    def _all(cls):
        "Grab all AWS instances"
        return [
            i for r in get_connection().get_all_instances()
            for i in r.instances
        ]


class security_groups(objects_base):
    "Singleton to stem off queries for security groups"

    @classmethod
    def _all(cls):
        "Grab all AWS Security Groups"
        return get_connection().get_all_security_groups()


class vpcs(objects_base):
    "Singleton to stem off queries for virtual private clouds"

    @classmethod
    def _all(cls):
        "Grab all AWS Virtual Private Clouds"
        return get_vpc_connection().get_all_vpcs()
