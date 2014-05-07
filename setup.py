#!/usr/bin/env python
"""
ec2
===

A light-weight wrapper around boto to query for AWS EC2 instances,
security groups, and VPCs in a sane way.
"""

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


install_requires = [
    'boto',
]

tests_require = [
    'mock',
    'pytest',
    'pytest-cov',
]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_suite = True

    def run_tests(self):
        import pytest
        import sys
        sys.exit(pytest.main(self.test_args))


setup(
    name='ec2',
    version='0.4.0',
    author='Matt Robenolt',
    author_email='matt@ydekproductions.com',
    url='https://github.com/mattrobenolt/ec2',
    description='Query for AWS EC2 instances, security groups, and VPCs simply',
    long_description=__doc__,
    packages=find_packages(exclude=('tests',)),
    install_requires=install_requires,
    tests_require=tests_require,
    license='BSD',
    cmdclass={'test': PyTest},
    test_suite='tests',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
    ],
)
