"""System checks for the requestlog settings"""
from django.conf import settings
from django.core.checks import Error

from .utils import is_valid_num_proxies


def check_settings(app_configs, **kwargs):
    errors = []
    num_proxies = getattr(settings, 'REQUEST_LOGGING_NUM_PROXIES', None)
    if not is_valid_num_proxies(num_proxies):
        errors.append(Error(
            f'REQUEST_LOGGING_NUM_PROXIES must be None or a non-negative integer, got {num_proxies!r}.',
            hint='Set it to the number of X-Forwarded-For entries your proxies append, or remove it.',
            id='requestlog.E001',
        ))
    return errors
