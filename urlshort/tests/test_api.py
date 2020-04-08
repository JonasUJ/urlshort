from django.test import TestCase

from ..settings import ALLOWED_HOSTS
from ..api import *
from ..models import *
from ..link_actions import get_id


class MockRequest:
    method = 'POST'
    scheme = 'https'
    META = {
        'HTTP_HOST': ALLOWED_HOSTS[0]
    }


class ApiTestCase(TestCase):
    request = MockRequest()

    def setUp(self):
        active = ShortUrlActive()
        active.save()

        # pylint: disable=no-member
        urlkey = ShortUrlKey.objects.create(keyhash=make_password('test'))

        # pylint: disable=no-member
        self.url = ShortUrl.objects.create(
            pk=get_id('test'),
            link='https://example.com',
            active=active,
            urlkey=urlkey
        )


class TestErrorSuccess(ApiTestCase):
    def test_success(self):
        self.assertDictEqual(
            success(self.request, self.url),
            {'status': 'success',
                'error_code': 0,
                'name': self.url.name,
                'link': self.url.link,
                'short': format_short(self.request, self.url.name),
                'created_at': self.url.created_at,
                'edited_at': self.url.edited_at,
                'uses': self.url.uses,
                'safe': self.url.is_safe,
                'active': {
                    'is_active': self.url.active.is_active,
                    'reason': self.url.active.reason,
                    'deactivated_since': self.url.active.deactivated_since},
                'key': False})

    def test_error(self):
        self.assertDictEqual(
            error(2, 'test'),
            {'status': 'error',
                'error_code': 2,
                'message': 'url with name \'test\' does not exist'})
        self.assertDictEqual(
            error(7, 'test'),
            {'status': 'error',
                'error_code': 7,
                'message': '\'test\' is not an allowed link'})


class TestRetrieve(ApiTestCase):
    def test_exists(self):
        self.assertDictEqual(
            retrieve(self.request, {'urlname': 'test'}),
            success(self.request, self.url))


class TestCreate(ApiTestCase):
    def test_invalid_name(self):
        self.assertDictEqual(
            create(self.request, {'urlname': '!nval!d',
                                  'link': 'https://example.com'}),
            error(6, '!nval!d'))

    def test_exists(self):
        self.assertDictEqual(
            create(self.request, {'urlname': 'test',
                                  'link': 'https://example.com'}),
            error(3, 'test'))

    def test_success(self):
        resp = create(
            self.request, {'urlname': 'new', 'link': 'https://example.com'})
        self.assertEqual(resp['error_code'], 0)


class TestEdit(ApiTestCase):
    def test_newlink(self):
        self.assertEqual(
            edit(self.request, {'urlname': 'test',
                                'newlink': 'https://example.org',
                                'key': 'test'})['link'],
            'https://example.org')

    def test_newkey(self):
        self.assertEqual(
            edit(self.request, {'urlname': 'test',
                                'newkey': 'testkey',
                                'key': 'test'})['key'],
            'testkey')

    def test_active(self):
        self.assertFalse(
            edit(self.request, {'urlname': 'test',
                                'active': 'false',
                                'key': 'test'})['active']['is_active'])
        self.assertTrue(
            edit(self.request, {'urlname': 'test',
                                'active': 'true',
                                'key': 'test'})['active']['is_active'])

    def test_reason(self):
        self.assertEqual(
            edit(self.request, {'urlname': 'test',
                                'reason': 'test',
                                'active': 'false',
                                'key': 'test'})['active']['reason'],
            'test')

    def test_max_reason(self):
        self.assertDictEqual(
            edit(self.request, {'urlname': 'test',
                                'active': 'false',
                                'reason': '_'*257,
                                'key': 'test'}),
            error(9))

    def test_wrong_key(self):
        self.assertDictEqual(
            edit(self.request, {'urlname': 'test',
                                'newkey': '',
                                'key': 'wrong key'}),
            error(8))


class TestDelete(ApiTestCase):
    def test_delete(self):
        delete(self.request, {'urlname': 'test', 'key': 'test'})
        # pylint: disable=no-member
        self.assertFalse(ShortUrl.objects.filter(pk=get_id('test')).exists())

    def test_not_exists(self):
        self.assertDictEqual(
            delete(self.request, {'urlname': 'not_exists', 'key': 'test'}),
            error(2, 'not_exists'))

    def test_wrong_key(self):
        self.assertDictEqual(
            delete(self.request, {'urlname': 'test', 'key': 'wrong key'}),
            error(8))

