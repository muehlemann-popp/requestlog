"""Middleware that creates log records"""

import logging
import re

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from httplib2 import Response

from .models import RequestLog
from .utils import replace_dict_values, get_client_ip

LOG = logging.getLogger(__name__)


class RequestLoggingMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.request = request
        self.ip_addr = get_client_ip(request)

        if not getattr(settings, 'REQUEST_LOGGING_ENABLED', False) or self._is_ignored_ip()\
            or self._is_ignored_url():
            return self.get_response(request)

        self.log = RequestLog()
        self.log_request(request)

        response = self.get_response(request)

        try:
            self.log_response(request, response)
            self.log.save()
        except Exception as e:
            # We catch all exceptions because if logging breaks the rest should still work
            msg = u'exception in the request logging {}'.format(e)
            LOG.critical(msg.encode('utf-8'))

        return response

    def _is_ignored_ip(self):
        ignored_ips = getattr(settings, 'REQUEST_LOGGING_IGNORE_IPS', [])
        if isinstance(ignored_ips, str):
            ignored_ips = [ignored_ips]
        return self.ip_addr in ignored_ips

    def _is_ignored_url(self):
        ignored_urls_re = getattr(settings, 'REQUEST_LOGGING_IGNORE_PATHS', [])
        if isinstance(ignored_urls_re, str):
            ignored_urls_re = [ignored_urls_re]
        regexes = [ re.compile(r) for r in ignored_urls_re ]
        return any(regex.match(self.request.path) for regex in regexes)

    @classmethod
    def clean_data(cls, raw_dict):
        """ Replace variables containing sensitive data """
        hide_parameters = getattr(settings, 'REQUEST_LOGGING_HIDE_PARAMETERS', [])
        if isinstance(hide_parameters, str):
            hide_parameters = [hide_parameters]

        replace_dict_values(
            raw_dict,
            hide_parameters,
            '********'
        )
        return raw_dict

    def log_request(self, request: WSGIRequest):
        """ logs request data """

        self.log.ip_addr = self.ip_addr
        self.log.url = request.path
        self.log.query =  self.clean_data(request.GET.copy())
        self.log.body = request.body[:1024]
        if hasattr(request, 'session'):
            self.log.session_key = request.session.session_key
        self.log.method = request.method
        headerdict = {k: v for k, v in request.META.items() if k.startswith('HTTP_')}
        self.log.headers = self.clean_data(headerdict)
        self.log.cookies = request.COOKIES

    def log_response(self, request: WSGIRequest, response: Response):
        self.log.status_code = getattr(response, 'status_code')
        if hasattr(response, "content"):
            if "decode" in dir(response.content): # type: ignore
                self.log.response_snippet = response.content.decode("utf-8")[0:256] # type: ignore
            else:
                self.log.response_snippet = response.content[0:256] # type: ignore
        # DRF populates the user object after all middlewares. Hence we log only here
        user = getattr(request, 'user', None)
        if user and ((callable(user.is_authenticated) and user.is_authenticated()) \
            or user.is_authenticated):
                self.log.user = user

