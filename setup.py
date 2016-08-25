#!/usr/bin/env python2.7

from setuptools import setup

setup (
    name = 'bap',
    version = '1.0.0',
    description = 'Python bindings to Binary Analysis Platform (BAP)',
    author = 'BAP Team',
    url = 'https://github.com/BinaryAnalysisPlatform/bap-python',
    maintainer = 'Ivan Gotovchits',
    maintainer_email = 'ivg@ieee.org',
    license = 'MIT',
    package_dir = {'bap' : 'src'},
    packages = ['bap'],
    extras_require = {
        'rpc' : ['requests']
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Disassemblers',
        'Topic :: Security'
    ]
)
