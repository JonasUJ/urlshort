from django.core.mail import EmailMessage

from .models import ShortUrl
from .settings import EMAIL_HOST_USER
from .link_actions import get_id


EMAIL_CONTACT_FORMAT = """
Afsender: {}
Afsender email: {}
Emne: {}
Besked: {}"""

ERRORS_API = (
    '',
    'could not determine action based on passed parameters (are you missing \'key\'?)',
    'url with name \'{}\' does not exist',
    'url with name \'{}\' already exists',
    '\'{}\' is not a valid URL',
    '\'{}\' does not point to a reachable address',
    '\'{}\' contains illegal characters or is too long',
    '\'{}\' is not an allowed link',
    'wrong key',
    'max length of 256 for \'reason\' exceeded',
    'cannot edit the link of an unsafe picourl'
)

ERRORS_HUMAN = (
    '',
    'Der skete en ukendt fejl.',
    'En picourl med det navn eksistere ikke.',
    'En picourl med det navn eksistere allerede.',
    'Linket er ikke en valid URL',
    'Serveren bag linket svarer ikke',
    'Navnet er ikke tilladt',
    'Linket er ikke tilladt',
    'Forkert nøgle',
    'Den maksimale længde af begrundelsen er opnået',
    'Linket på en usikker picourl kan ikke ændres'
)


def send_contact_email(contact_form):
    mail = EmailMessage(
        f'[Picourl/Contact] {contact_form.cleaned_data.get("emne", "ikke angivet")}',
        EMAIL_CONTACT_FORMAT.format(
            contact_form.cleaned_data.get("navn", "ikke angivet"),
            contact_form.cleaned_data.get("email"),
            contact_form.cleaned_data.get("emne", "ikke angivet"),
            contact_form.cleaned_data.get("besked")),
        to=[EMAIL_HOST_USER])
    mail.send(False)


def urlname_exists(urlname):
    # pylint: disable=no-member
    return ShortUrl.objects.filter(pk=get_id(urlname)).exists()
