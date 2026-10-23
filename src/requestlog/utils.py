"""Utilities for the django_request_logging module"""
from datetime import datetime, timedelta
from typing import Any, Optional

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv46_address
from django.http import HttpRequest
from django.utils import timezone

from .models import RequestLog

def replace_dict_values(the_dict, keys, replacement):
    """
    replaces values in dictionary for keys
    if present in the dictionary
    """
    for key in keys:
        if key in the_dict:
            the_dict[key] = replacement


def get_client_ip(request: HttpRequest) -> Optional[str]:
    """
    Returns the client IP from the X-Forwarded-For entry selected by REQUEST_LOGGING_NUM_PROXIES.
    Falls back to REMOTE_ADDR if the header is missing, has fewer entries than proxies,
    the selected entry is not a valid IP address or the setting is invalid.
    """
    remote_addr = request.META.get('REMOTE_ADDR')
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    num_proxies = getattr(settings, 'REQUEST_LOGGING_NUM_PROXIES', None)
    if not x_forwarded_for or not is_valid_num_proxies(num_proxies) or num_proxies == 0:
        return remote_addr

    entries = [entry.strip() for entry in x_forwarded_for.split(',')]
    if num_proxies is None:
        # The leftmost entry is set by the client and can be anything
        ip = entries[0]
    elif num_proxies <= len(entries):
        ip = entries[-num_proxies]
    else:
        return remote_addr

    return ip if _is_valid_ip(ip) else remote_addr


def is_valid_num_proxies(value: Any) -> bool:
    # bool is a subclass of int, so it has to be rejected explicitly
    return value is None or (isinstance(value, int) and not isinstance(value, bool) and value >= 0)


def _is_valid_ip(value: str) -> bool:
    # Use the validator of the GenericIPAddressField the IP is stored in, so we accept exactly what it accepts
    try:
        validate_ipv46_address(value)
    except ValidationError:
        return False
    return True


def delete_old_entries(older_than_days=30):
    """
    Delete old entries
    :param older_than_days: Delete tasks older than this amount of days
    :return: number of deleted rows
    """
    import logging
    since = timezone.now() - timedelta(days=older_than_days)
    entries = RequestLog.objects.filter(timestamp__lte=since)
    log = logging.getLogger(__name__)
    log.info(f"Remove {entries.count()} Old Requestlog entries older than {since.strftime('%d.%m.%Y')}")
    (deleted, rowcount) = entries.delete()
    log.info(f"Deleted {deleted} rows")
    return deleted
