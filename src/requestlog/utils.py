"""Utilities for the django_request_logging module"""
from datetime import datetime, timedelta
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


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


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
