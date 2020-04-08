from django.test import TestCase

from ..settings import ALLOWED_HOSTS
from ..link_actions import *


class LinkActionsTest(TestCase):
    def test_validate_link(self):
        self.assertTrue(validate_link('https://picourl.dk/'))
        self.assertTrue(validate_link('http://255.255.255.00/'))
        self.assertFalse(validate_link('picourl.dk'))

    def test_is_reachable(self):
        assert True

    def test_get_shortened(self):
        self.assertEqual(get_shortened(64**4), '10000')
        self.assertEqual(get_shortened(64**5-1), '-----')
        self.assertEqual(get_shortened(64**5/2), 'w0000')

    def test_get_id(self):
        self.assertEqual(get_id('10000'), 64**4)
        self.assertEqual(get_id('-----'), 64**5-1)
        self.assertEqual(get_id('w0000'), 64**5/2)

    def test_only_allowed_chars(self):
        self.assertTrue(only_allowed_chars(
            '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-'))
        self.assertFalse(only_allowed_chars('+'))
        self.assertFalse(only_allowed_chars('#'))
        self.assertFalse(only_allowed_chars('/'))
        self.assertFalse(only_allowed_chars('?'))

    def test_is_host_self(self):
        self.assertTrue(is_host_self(f'https://{ALLOWED_HOSTS[0]}/path?query'))
        self.assertFalse(is_host_self('https://example.com'))

    def test_is_picourl(self):
        self.assertTrue(is_picourl(f'https://{ALLOWED_HOSTS[0]}/+test'))
        self.assertTrue(is_picourl(
            f'https://{ALLOWED_HOSTS[0]}/+test?test=test#test'))
        self.assertFalse(is_picourl(f'https://{ALLOWED_HOSTS[0]}/test'))

    def test_format_short(self):
        def request(_): return ...  # "Empty" object
        request.scheme = 'https'
        request.META = {'HTTP_HOST': ALLOWED_HOSTS[0]}
        self.assertEqual(format_short(request, 'test'),
                         f'https://{ALLOWED_HOSTS[0]}/+test')

    def test_get_urlname(self):
        self.assertEqual(get_urlname(
            f'https://{ALLOWED_HOSTS[0]}/+test'), 'test')
        self.assertFalse(get_urlname(f'https://{ALLOWED_HOSTS[0]}/test'))

