#!/usr/bin/env python
"""
ec2
======

A light weight wrapper around boto to query for AWS EC2 instances in a sane way.
"""

from setuptools import setup

setup(
    name='ec2',
    version='0.0.1',
    author='Matt Robenolt',
    author_email='matt@ydekproductions.com',
    url='https://github.com/mattrobenolt/ec2',
    description='Query for EC2 instances simply',
    long_description=__doc__,
    py_modules=['ec2'],
    install_requires=[
        'boto'
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
