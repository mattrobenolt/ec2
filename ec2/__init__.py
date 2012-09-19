"""
ec2
~~~~~

:copyright: (c) 2012 by Matt Robenolt.
:license: BSD, see LICENSE for more details.
"""

__author__ = 'Matt Robenolt <matt@ydekproductions.com>'
__version__ = '0.2.0'
__license__ = 'BSD'
__all__ = ('credentials', 'instances', 'security_groups')

from .connection import credentials
from .types import instances, security_groups
