#!/usr/bin/env python

import os

from setuptools import find_packages, setup

'''
Learn more about packaging here:
https://packaging.python.org/distributing/#setup-args
'''

README = ''
readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
if os.path.exists(readme_path):
    with open(readme_path) as readme:
        README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='requestlog',
    version='1.0.0',
    description='Middleware to log http requests to the database',
    long_description=README,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=1.9',
        'psycopg2',
        'coverage',
        'flake8',
        'pep8',
        'polib~=1.0',
        'django-environ'
    ],
    url='https://gitlab.com/mpom/requestlog',
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
    author='Silvan Mühlemann',
    author_email='silvan.muehlemann@muehlemann-popp.ch',
    license='License :: Other/Proprietary License',
)
