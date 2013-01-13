#!/usr/bin/env python

# Bootstrap installation of Distribute
import distribute_setup
distribute_setup.use_setuptools()

import os

from setuptools import setup


PROJECT = u'screp'
VERSION = '0.2'
URL = ''
AUTHOR = u'Doru Arfire'
AUTHOR_EMAIL = u'doruarfire@gmail.com'
DESC = "A short description..."

requires = [
        'pyparsing',
        'lxml',
        ]

def read_file(file_name):
    file_path = os.path.join(
        os.path.dirname(__file__),
        file_name
        )
    return open(file_path).read()

setup(
    name=PROJECT,
    version=VERSION,
    description=DESC,
    long_description=read_file('README.rst'),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=read_file('LICENSE'),
    namespace_packages=[],
    packages=[u'screp'],
#    package_dir = {'': os.path.dirname(__file__)},
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points = {
        'console_scripts': [
            'screp=screp.main:main',
            ],
        # -*- Entry points -*-
    },
    classifiers=[
    	# see http://pypi.python.org/pypi?:action=list_classifiers
        # -*- Classifiers -*- 
        'License :: OSI Approved',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        "Programming Language :: Python",
    ],
)
