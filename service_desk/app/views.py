from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template

# from .utils import check_if_user_logged


def home(request, template_name='home.html'):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}')
    return render(request, template_name, {'test_var': 'hello'}, status=200)


def password_change(request, template_name='password-change.html'):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}?next={request.path}')
    return render(request, template_name, {}, status=200)


def logged_out(request, template_name='logged-out.html'):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse(home))
    return render(request, template_name, {}, status=200)


def bad_request(request, exception=None, template_name='errors/400.html'):
    return render(request, template_name, {}, status=400)


def permission_denied(request, exception=None, template_name='error/403.html'):
    return render(request, template_name, {}, status=403)


def page_not_found(request, exception=None, template_name='errors/404.html'):
    return render(request, template_name, {}, status=404)


def internal_server_error(request, exception=None, template_name='error/500.html'):
    return render(request, template_name, {}, status=500)


def test(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}?next={request.path}')
    return HttpResponse('logged - test')


#def login(TemplateView):
#    template_name = 'login.html'
#    redirect_authenticated_user = True
    #if request.user.is_authenticated:
    #    return HttpResponseRedirect(reverse(home))
    #return render(request, template_name, {}, status=201)
#    return TemplateView(template_name, redirect_authenticated_user)

