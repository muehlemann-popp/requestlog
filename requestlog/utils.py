"""Utilities for the django_request_logging module"""

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
