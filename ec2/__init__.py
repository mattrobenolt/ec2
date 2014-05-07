"""
ec2
~~~

:copyright: (c) 2014 by Matt Robenolt.
:license: BSD, see LICENSE for more details.
"""

try:
    __version__ = __import__('pkg_resources') \
        .get_distribution('ec2').version
except Exception:  # pragma: no cover
    __version__ = 'unknown'

__author__ = 'Matt Robenolt <matt@ydekproductions.com>'
__license__ = 'BSD'
__all__ = ('credentials', 'instances', 'security_groups', 'vpcs')

from .connection import credentials  # noqa
from .types import instances, security_groups, vpcs  # noqa
