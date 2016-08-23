#!/usr/bin/env python2.7

from setuptools import setup

setup (
    name = 'bap',
    version = '1.0.0~alpha',
    package_dir = {'bap' : 'src'},
    packages = ['bap'],
    install_requires = ['requests']
)
