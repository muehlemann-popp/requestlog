import os
import unittest

from django.core.checks import run_checks
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, TestCase

from ..checks import check_settings
from ..middleware import RequestLoggingMiddleware
from ..models import RequestLog
from ..utils import get_client_ip


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

    def test_invalid_x_forwarded_for_logs_remote_addr(self):
        with self.settings(REQUEST_LOGGING_ENABLED=True):
            request = self.factory.get('/wordpress/', HTTP_X_FORWARDED_FOR='localhost', REMOTE_ADDR='192.0.2.1')
            self.middleware(request)
            self.assertEqual(list(RequestLog.objects.values_list('ip_addr', flat=True)), ['192.0.2.1'])

    def test_x_forwarded_for_rejected_by_the_ip_field_is_still_logged(self):
        # Python accepts IPv6 zone IDs of any length, Django rejects addresses longer than 39 characters
        with self.settings(REQUEST_LOGGING_ENABLED=True):
            request = self.factory.get('/', HTTP_X_FORWARDED_FOR='fe80::1%' + 'a' * 32)
            self.middleware(request)
            self.assertEqual(RequestLog.objects.count(), 1)

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


class GetClientIpTest(SimpleTestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def _get_client_ip(self, x_forwarded_for=None):
        extra = {'REMOTE_ADDR': '192.0.2.1'}
        if x_forwarded_for is not None:
            extra['HTTP_X_FORWARDED_FOR'] = x_forwarded_for
        return get_client_ip(self.factory.get('/', **extra))

    def test_uses_remote_addr_without_x_forwarded_for(self):
        self.assertEqual(self._get_client_ip(), '192.0.2.1')

    def test_uses_leftmost_x_forwarded_for_entry_by_default(self):
        self.assertEqual(self._get_client_ip('203.0.113.7, 198.51.100.1'), '203.0.113.7')

    def test_falls_back_to_remote_addr_when_entry_is_not_an_ip(self):
        self.assertEqual(self._get_client_ip('localhost, 198.51.100.1'), '192.0.2.1')

    def test_num_proxies_selects_entry_appended_by_the_proxies(self):
        with self.settings(REQUEST_LOGGING_NUM_PROXIES=2):
            self.assertEqual(self._get_client_ip('localhost, 203.0.113.7, 198.51.100.1'), '203.0.113.7')

    def test_num_proxies_equal_to_the_entry_count_selects_the_leftmost_entry(self):
        with self.settings(REQUEST_LOGGING_NUM_PROXIES=2):
            self.assertEqual(self._get_client_ip('203.0.113.7, 198.51.100.1'), '203.0.113.7')

    def test_num_proxies_accepts_ipv6_entries(self):
        with self.settings(REQUEST_LOGGING_NUM_PROXIES=1):
            self.assertEqual(self._get_client_ip('203.0.113.7, 2001:db8::1'), '2001:db8::1')

    def test_num_proxies_zero_ignores_x_forwarded_for(self):
        with self.settings(REQUEST_LOGGING_NUM_PROXIES=0):
            self.assertEqual(self._get_client_ip('203.0.113.7'), '192.0.2.1')

    def test_falls_back_to_remote_addr_when_there_are_fewer_entries_than_proxies(self):
        # The header did not pass through all proxies, so even its rightmost entry may come from the client
        with self.settings(REQUEST_LOGGING_NUM_PROXIES=2):
            self.assertEqual(self._get_client_ip('203.0.113.7'), '192.0.2.1')

    def test_invalid_num_proxies_falls_back_to_remote_addr(self):
        # System checks don't run under gunicorn & co, so a misconfiguration must not break requests
        for value in (-1, '2', True):
            with self.subTest(value=value), self.settings(REQUEST_LOGGING_NUM_PROXIES=value):
                self.assertEqual(self._get_client_ip('203.0.113.7'), '192.0.2.1')


class SettingsCheckTest(SimpleTestCase):

    def test_accepts_valid_num_proxies(self):
        for value in (None, 0, 2):
            with self.subTest(value=value), self.settings(REQUEST_LOGGING_NUM_PROXIES=value):
                self.assertEqual(check_settings(None), [])

    def test_rejects_invalid_num_proxies(self):
        for value in (-1, '2', True):
            with self.subTest(value=value), self.settings(REQUEST_LOGGING_NUM_PROXIES=value):
                self.assertEqual([error.id for error in check_settings(None)], ['requestlog.E001'])

    def test_check_is_registered(self):
        with self.settings(REQUEST_LOGGING_NUM_PROXIES=-1):
            self.assertIn('requestlog.E001', [error.id for error in run_checks()])
