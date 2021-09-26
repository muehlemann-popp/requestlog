import os
import unittest

from django.test import TestCase

from django.http import HttpResponse
from django.test import RequestFactory
from ..middleware import RequestLoggingMiddleware
from ..models import RequestLog


class RequestlogMiddlewareTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RequestLoggingMiddleware(RequestlogMiddlewareTest._get_response)

    @staticmethod
    def _get_response(request):
        response = HttpResponse("1" * 1000)
        response.status_code = 205
        return response

    def test_request_logging_can_be_disabled(self):
        with self.settings(REQUEST_LOGGING_ENABLED=False):
            request = self.factory.get('/customer/details?foo=bar')
            self.middleware(request)
            self.assertEqual(RequestLog.objects.all().count(), 0)

    def test_ips_can_be_ignored(self):
        # positive case
        with self.settings(REQUEST_LOGGING_ENABLED=True, REQUEST_LOGGING_IGNORE_IPS=['1.2.3.4']):
            request = self.factory.get('/customer/details')
            request.META['REMOTE_ADDR'] = '1.2.3.4'
            self.middleware(request)
            self.assertEqual(RequestLog.objects.all().count(), 0)

    def test_ips_can_be_ignored2(self):
        # negative case
        with self.settings(REQUEST_LOGGING_ENABLED=True, REQUEST_LOGGING_IGNORE_IPS=['1.2.3.5']):
            request = self.factory.get('/customer/details')
            request.META['REMOTE_ADDR'] = '1.2.3.4'
            self.middleware(request)
            self.assertEqual(RequestLog.objects.all().count(), 1)

    def test_urls_can_be_ignored(self):
        # positive case
        with self.settings(REQUEST_LOGGING_ENABLED=True, REQUEST_LOGGING_IGNORE_PATHS=['/foo/bar']):
            request = self.factory.get('/foo/bar?baz')
            self.middleware(request)
            self.assertEqual(RequestLog.objects.all().count(), 0)

        # negative case
        with self.settings(REQUEST_LOGGING_ENABLED=True, REQUEST_LOGGING_IGNORE_PATHS=[]):
            request = self.factory.get('/foo/bar')
            self.middleware(request)
            self.assertEqual(RequestLog.objects.all().count(), 1)

    def test_requestProcessing(self):
        with self.settings(REQUEST_LOGGING_ENABLED=True):
            request = self.factory.get('/customer/details?foo=bar', HTTP_SOME_HEADER='my header data',
                                       HEADER_TO_IGNORE='Ignore me')
            self.middleware(request)
            entries = RequestLog.objects.all()
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].url, '/customer/details')
            self.assertEqual(entries[0].method, 'GET')
            self.assertEqual(entries[0].query, {'foo': 'bar'})
            self.assertEqual(entries[0].status_code, 205)
            # Only the first 256 chars are stored.
            self.assertEqual(entries[0].response_snippet, "1" * 256)
            self.assertEqual(entries[0].headers, {'HTTP_COOKIE': '', 'HTTP_SOME_HEADER': 'my header data'})

    def test_requestFileUpload_does_not_store_content(self):
        with self.settings(REQUEST_LOGGING_ENABLED=True):
            request = self.factory.get('/')

            def get_file_response(request):
                from django.http import FileResponse
                response = FileResponse("1" * 1000)
                response.status_code = 200
                return response

            middleware = RequestLoggingMiddleware(get_file_response)
            middleware(request)
            entries = RequestLog.objects.all()
            self.assertEqual(len(entries), 1)
            self.assertIsNone(entries[0].response_snippet)

    @unittest.skipIf(os.environ.get('ENV'), "default")
    def test_secret_values_should_be_replaced(self):
        with self.settings(REQUEST_LOGGING_ENABLED=True):
            # Hiding disabled
            request = self.factory.post('/customer/details?secret=password', HTTP_HEADER_TO_HIDE='very secret')
            self.middleware(request)
            entries = RequestLog.objects.all()
            self.assertEqual(entries[0].headers, {'HTTP_HEADER_TO_HIDE': 'very secret', 'HTTP_COOKIE': ''})
            self.assertEqual(entries[0].query, {'secret': 'password'})

            # Hiding enabled
            with self.settings(REQUEST_LOGGING_HIDE_PARAMETERS=['HTTP_HEADER_TO_HIDE', 'secret']):
                request = self.factory.post('/customer/details?secret=password', HTTP_HEADER_TO_HIDE='very secret')
                self.middleware(request)
                entries = RequestLog.objects.all()
                self.assertEqual(entries[1].headers, {'HTTP_HEADER_TO_HIDE': '********', 'HTTP_COOKIE': ''})
                self.assertEqual(entries[1].query, {'secret': '********'})


class RequestlogUtilsTest(TestCase):
    def test_delete_old_entries(self):
        from django.utils import timezone
        from datetime import timedelta
        from ..utils import delete_old_entries
        RequestLog.objects.create(timestamp=timezone.now(), ip_addr='1.2.3.4', headers={})
        old_item = RequestLog.objects.create(ip_addr='1.2.3.4', headers={})
        old_item.timestamp=timezone.now() - timedelta(days=60)
        old_item.save()

        delete_old_entries(older_than_days=30)
        self.assertEqual(1, RequestLog.objects.all().count())
