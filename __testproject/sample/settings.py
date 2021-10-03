# -*- coding: utf-8
"""
Settings for test.
"""
from __future__ import unicode_literals, absolute_import
import os

DEBUG = True
USE_TZ = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "**************************************************"

# Note, this package only works with PostgreSQL due to the JSONField
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
    }
}

ROOT_URLCONF = "sample.urls"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    'requestlog.apps.AppConfig'
]

REQUEST_LOGGING_IGNORE_IPS = []
REQUEST_LOGGING_IGNORE_PATHS = []
REQUEST_LOGGING_HIDE_PARAMETERS = []
