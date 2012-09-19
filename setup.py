#!/usr/bin/env python
"""
ec2
======

A light-weight wrapper around boto to query for AWS EC2 instances
and security groups in a sane way.
"""

from setuptools import setup, find_packages

setup(
    name='ec2',
    version='0.2.0',
    author='Matt Robenolt',
    author_email='matt@ydekproductions.com',
    url='https://github.com/mattrobenolt/ec2',
    description='Query for AWS EC2 instances and security groups simply',
    long_description=__doc__,
    packages=find_packages(),
    install_requires=[
        'boto'
    ],
    tests_require=[
        'nose',
        'mock',
    ],
    test_suite='tests',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
