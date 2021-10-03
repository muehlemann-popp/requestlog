#!/usr/bin/env python

import os
import setuptools

README = ''
readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
if os.path.exists(readme_path):
    with open(readme_path) as readme:
        README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setuptools.setup(
    name='django-requestlog',
    version='1.1.7',
    description='Middleware to log http requests to postgresql',
    long_description=README,
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    long_description_content_type="text/markdown",
    url="https://github.com/muehlemann-popp/requestlog",
    include_package_data=True,
    install_requires=[
        'Django>=1.9',
        'httplib2',
        'psycopg2-binary',
    ],
    tests_require=['coverage'],
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
    author='Silvan Mühlemann',
    author_email='silvan.muehlemann@muehlemann-popp.ch',
    license='MIT',
)
