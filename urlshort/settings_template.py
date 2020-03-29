# This is a template for the settings.py file used in this project

# pylint: disable=unused-wildcard-import
from .settings_public import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

if DEBUG:
    ALLOWED_HOSTS = ['']
else:
    ALLOWED_HOSTS = ['']

# Email config
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.example.com'
EMAIL_HOST_USER = 'example@example.com'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = '******'
EMAIL_PORT = 587
EMAIL_USE_SSL = False
EMAIL_ADMIN_USER = 'admin@example.com'

# VirusTotal
VIRUSTOTAL_API_KEY = ''