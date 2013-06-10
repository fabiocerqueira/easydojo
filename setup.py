#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

import easydojo

setup(
    name='easydojo',
    version=easydojo.__version__,
    author='Fábio Cerqueira',
    author_email='cerqueirasfabio@gmail.com',
    maintainer="Fábio Cerqueira",
    maintainer_email="cerqueirasfabio@gmail.com",
    url='http://github.com/fabiocerqueira/easydojo',
    install_requires=[
        'clint>=0.3',
        'docopt>=0.6',
        'watchdog>=0.6',
    ],
    description = 'Simple tools developed to help in Coding Dojo sessions',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['LICENSE']},
    license=open('LICENSE').read(),
    scripts=['easydojo.py'],
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "License :: OSI Approved :: Apache Software License",
    ],
)
