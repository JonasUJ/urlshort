import json

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.views.decorators.http import require_safe, require_http_methods
from django.views.decorators.csrf import csrf_exempt

from . import models, utils
from .link_actions import get_urlname, is_picourl
from .settings import EMAIL_HOST_USER, EMAIL_ADMIN_USER
from .api import responseFromQuery, retrieve, edit, delete
from .forms import ContactForm, LookupEditForm


@require_http_methods(['GET', 'POST', 'HEAD'])
def main(request):
    return render(request, 'main_page.html')


@require_safe
def link(request, name):
    try:
        # pylint: disable=no-member
        url = models.ShortUrl.objects.get(name=name)
    except ObjectDoesNotExist:
        return handler404(request, 'nourl', name=name)

    if not url.active.is_active:
        return render(request, 'deactivated_page.html')

    if url.is_safe == models.SafeState.NO:
        return render(request, 'unsafe_page.html', {'link': url.link})

    url.uses += 1
    url.save()
    return redirect(url)


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def api(request):
    query = request.GET or request.POST
    if query:
        return JsonResponse(responseFromQuery(request, query.dict()))
    elif request.method == 'POST' and request.body:
        try:
            query = json.loads(request.body)
        except json.JSONDecodeError:
            return render(request, 'api_page.html')
        return JsonResponse(responseFromQuery(request, query))
    else:
        return render(request, 'api_page.html')


@require_safe
def about(request):
    return render(request, 'about_page.html')


@require_http_methods(['GET', 'POST', 'HEAD'])
def lookup(request):
    urlname = request.GET.get('urlname')
    data = {}
    error_msg = ''
    success = False
    form = LookupEditForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            submit = request.POST.get('submit', '')
            success = True
            res = {}
            if submit == 'submit':
                res = edit(request, {
                        'urlname': urlname,
                        'newlink': form.cleaned_data['link'],
                        'key': form.cleaned_data['nøgle']})
            elif submit == 'delete':
                res = delete(request, {
                        'urlname': urlname,
                        'key': form.cleaned_data['nøgle']})
            elif submit == 'activate':
                res = edit(request, {
                        'urlname': urlname,
                        'active': 'true',
                        'reason': '',
                        'key': form.cleaned_data['nøgle']})
            elif submit == 'deactivate':
                res = edit(request, {
                        'urlname': urlname,
                        'active': 'false',
                        'reason': 'Deaktiveret af ejer',
                        'key': form.cleaned_data['nøgle']})
            else:
                success = False
                error_msg = 'Der skete en ukendt fejl.'

            if success and res.get('error_code', 0) != 0:
                error_msg = utils.ERRORS_HUMAN[res['error_code']]

    if urlname:
        if is_picourl(urlname):
            urlname = get_urlname(urlname)

        data = retrieve(request, {'urlname': urlname})

        if data['error_code'] == 2:
            return handler404(request, 'nourl', urlname)

        form = LookupEditForm(
            request.POST or None,
            request.FILES or None,
            initial={
                'link': data['link'] if data['active']['is_active'] else '',
                'antal_besøg': data['uses'],
                'oprettet': data['created_at'],
                'redigeret': data.get('edited_at', ''),
                'deaktiveret_siden': data.get('deactivated_since', '')})

    return render(request, 'lookup_page.html', {
        'urlname': urlname,
        'data': data,
        'form': form,
        'error': error_msg,
        'success': success})


@require_http_methods(['GET', 'POST', 'HEAD'])
def contact(request):
    success = False
    form = ContactForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            try:
                utils.send_contact_email(form)
            except Exception:
                return handler500(request)
            success = True

    return render(request, 'contact_page.html', {
        'success': success,
        'form': form,
        'admin': EMAIL_ADMIN_USER})


def handler404(request, exception, name=''):
    resp = render(request, 'error_page.html', {
        'error_code': 404,
        'name': name,
        'error_msg': 'Picourl ikke fundet' if exception == 'nourl' else 'Siden findes ikke'})
    resp.status_code = 404
    return resp


def handler500(request):
    resp = render(request, 'error_page.html', {
        'error_code': 500,
        'error_msg': 'Intern serverfejl'})
    resp.status_code = 500
    return resp
