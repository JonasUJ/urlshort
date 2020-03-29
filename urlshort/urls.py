"""urlshort URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path

from .views import (main, link, api, about, lookup,
                    contact, handler404, handler500)


urlpatterns = [
    path('admin', admin.site.urls, name='admin'),
    path('', main, name='main'),
    re_path(r'^\+(?P<name>[\w\-]+)$', link, name='link'),
    re_path(r'^about/?$', about, name='about'),
    re_path(r'^api/?$', api, name='api'),
    re_path(r'^lookup/?$', lookup, name='lookup'),
    re_path(r'^contact/?$', contact, name='contact'),
]

handler404 = handler404
handler500 = handler500
