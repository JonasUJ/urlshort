import re
from base64 import b64encode
from urllib.parse import urlsplit

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from .settings import ALLOWED_HOSTS

ALLOWED_CHARS_STRING = r'[\w\-]*'
ALLOWED_CHARS_RE = re.compile(f'^{ALLOWED_CHARS_STRING}$')
_PORT = r'(:\d{1,5})?'
URLNAME_RE = re.compile(
    f'^(https?)://({"|".join(re.escape(host)+_PORT for host in ALLOWED_HOSTS)})/\\+(?P<urlname>{ALLOWED_CHARS_STRING})$')


def validate_link(link):
    try:
        URLValidator()(link)
    except ValidationError:
        return False
    return True


def is_reachable(link):
    return True


def get_shortened(url):
    return b64encode(str(url.id).encode('utf-8'), b'-_').decode('utf-8').rstrip('=')


def only_allowed_chars(name):
    return not ALLOWED_CHARS_RE.match(name) is None


def is_host_self(host):
    for ahost in ALLOWED_HOSTS:
        if ahost in host:
            return True
    return False


def is_picourl(url):
    split = urlsplit(url)
    pathonly = f'{split.scheme}://{split.netloc}{split.path}'
    if is_host_self(split.netloc) and URLNAME_RE.match(pathonly):
        return True
    return False


def format_short(request, name):
    return f'{request.scheme}://{request.META["HTTP_HOST"]}/+{name}'


def get_urlname(url):
    match = URLNAME_RE.match(url)
    if match:
        return match.group('urlname')
    return False
