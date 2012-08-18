#!/usr/bin/env python
from setuptools import setup
import sys
import platform

__VERSION__ = "0.1" 

requires=[]

scripts = ['rst2twiki.py', 'rst2wiki.py', ]

setup(
    name = "rst2twiki",
    version = __VERSION__,
    url = 'https://github.com/idning/rst2twiki',
    author = 'ning',
    author_email = 'idning@gmail.com',
    description = "reStructuredText to twiki",
    #packages = ['xxx'],
    include_package_data = True,
    install_requires = requires,
    scripts = scripts,
    classifiers = ['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'License :: OSI Approved :: GNU Affero General Public License v3',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   ],
)

