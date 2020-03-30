from random import randrange
from secrets import token_urlsafe
from datetime import datetime

from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from .utils import urlname_exists, ERRORS_API
from .settings import URLNAME_LENGTH
from .models import ShortUrl, ShortUrlActive, ShortUrlKey, SafeState
from .link_actions import (
    validate_link,
    is_reachable,
    format_short,
    get_shortened,
    only_allowed_chars,
    is_picourl
)

RANGE_LOWER = 64**(URLNAME_LENGTH-1)
RANGE_UPPER = 64**URLNAME_LENGTH


def responseFromQuery(request, query):
    if 'link' in query and request.method == 'POST':
        return create(request, query)
    elif 'key' in query and 'urlname' in query and request.method == 'POST':
        if 'delete' in query:
            return delete(request, query)
        elif 'active' in query or 'newlink' in query or 'newkey' in query:
            return edit(request, query)
    elif 'urlname' in query and request.method == 'GET':
        return retrieve(request, query)
    return error(1)


def error(errno, *to_format):
    return {
        'status': 'error',
        'error_code': errno,
        'message': ERRORS_API[errno].format(*to_format)
    }


def success(request, url, key=False):
    return {
        'status': 'success',
        'error_code': 0,
        'name': url.name,
        'link': url.link,
        'short': format_short(request, url.name),
        'created_at': url.created_at,
        'edited_at': url.edited_at,
        'uses': url.uses,
        'safe': url.is_safe,
        'active': {
            'is_active': url.active.is_active,
            'reason': url.active.reason,
            'deactivated_since': url.active.deactivated_since
        },
        'key': key
    }


def retrieve(request, query):
    try:
        # pylint: disable=no-member
        url = ShortUrl.objects.get(name=query['urlname'])
    except ObjectDoesNotExist:
        return error(2, query["urlname"])

    return success(request, url)


def verify_link(link):
    if not validate_link(link):
        return False, error(4, link)

    elif is_picourl(link):
        return False, error(7, link)

    if not is_reachable(link):
        return False, error(5, link)

    return True, {}


def create(request, query):
    if not only_allowed_chars(query.get('urlname')):
        return error(6, query['urlname'])

    valid = verify_link(query['link'])
    if not valid[0]:
        return valid[1]

    if urlname_exists(query['urlname']):
        return error(3, query['urlname'])

    urlid = randrange(RANGE_LOWER, RANGE_UPPER)
    # pylint: disable=no-member
    while ShortUrl.objects.filter(id=urlid).exists():
        urlid = randrange(RANGE_LOWER, RANGE_UPPER)

    active = ShortUrlActive()
    active.save()

    tokenkey = query.get('key', token_urlsafe(16))
    # pylint: disable=no-member
    urlkey = ShortUrlKey.objects.create(
        keyhash=make_password(tokenkey))

    name_provided = query.get('urlname', '')

    # pylint: disable=no-member
    url = ShortUrl.objects.create(
        pk=urlid,
        link=query['link'],
        name=query['link'][:48] if not name_provided else query['urlname'],
        active=active,
        urlkey=urlkey
    )

    if not name_provided:
        url.name = get_shortened(url)
        url.save()

    return success(request, url, tokenkey)


def edit(request, query):
    reason = query.get('reason', '')
    active = query.get('active', '').lower()
    if active not in ('', 'true', 'false', '0', '1'):
        return error(1)
    elif len(reason) > 256:
        return error(9)

    newlink = query.get('newlink', '')
    if newlink:
        valid = verify_link(newlink)
        if not valid[0]:
            return valid[1]

    # pylint: disable=no-member
    shorturl = ShortUrl.objects.filter(name=query['urlname'])

    if not shorturl.exists():
        return error(2, query['urlname'])

    shorturl = shorturl[0]

    if not shorturl.urlkey.matches(query['key']):
        return error(8)

    if newlink:
        if shorturl.is_safe == SafeState.NO:
            return error(10)
        shorturl.link = newlink

    if active in ('false', '0'):
        if shorturl.active.is_active:
            shorturl.active.deactivated_since = timezone.now()
        shorturl.active.is_active = False
        shorturl.active.reason = reason
        shorturl.active.save()
    elif active in ('true', '1'):
        shorturl.active.is_active = True
        shorturl.active.deactivated_since = None
        shorturl.active.reason = reason
        shorturl.active.save()

    newkey = query.get('newkey', False)
    if not newkey is False:
        shorturl.urlkey.set_key(newkey)

    shorturl.save()
    return success(request, shorturl, newkey)


def delete(request, query):
    # pylint: disable=no-member
    shorturl = ShortUrl.objects.filter(name=query['urlname'])
    if not shorturl.exists():
        return error(2, query['urlname'])

    shorturl = shorturl[0]
    if not shorturl.urlkey.matches(query['key']):
        return error(8)

    shorturl.delete()
    return success(request, shorturl)
