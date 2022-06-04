from django.http import HttpResponse, HttpResponseRedirect
from django.http.cookie import SimpleCookie
from django.shortcuts import render, reverse
from django.conf import settings
from app.models import Tenant, Status
# from app.utils import get_user_type
from django.template.loader import get_template


def home(request, template_name='home.html'):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}')
    response = render(request, template_name, status=200)
    response.set_cookie(key='active_tenant_id', value=1)
    return response
    # return render(request, template_name, {'user_tenant_type': user_type}, status=200)


def create_ticket(request, template_name='create-ticket.html'):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}')
    response = render(request, template_name, status=200)
    return response


def password_change(request, template_name='password-change.html'):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}?next={request.path}')
    '''
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })
    '''
    return render(request, template_name, {}, status=200)


def password_reset(request, template_name='password-reset.html'):
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


#def login(TemplateView):
#    template_name = 'login.html'
#    redirect_authenticated_user = True
    #if request.user.is_authenticated:
    #    return HttpResponseRedirect(reverse(home))
    #return render(request, template_name, {}, status=201)
#    return TemplateView(template_name, redirect_authenticated_user)


'''
def change_password(request):
    
'''