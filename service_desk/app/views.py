from django.http import HttpResponseRedirect, HttpResponse
from django.http.cookie import SimpleCookie
from django.shortcuts import render, reverse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.signals import user_logged_out
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from .models import Board
from .forms import IssueForm
from .utils import get_session_tenant_type, get_env_type, get_initial_status, get_tenant, tenant_data_in_session, clear_tenant_session
from .context_processors import user_tenant_type


def home(request, template_name='home.html'):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}')
    else:
        if not tenant_data_in_session(request):
            request = user_tenant_type(request)
        #tenants = get_session_tenant_deserialized(request)
        boards = Board.objects.all()
        # issues = get_active_tenant_issues(request)
        # response = render(request, template_name,  status=200)
        # response.set_cookie(key='active_tenant_id', value=1)
        return render(request, template_name,  status=200)
        # return render(request, template_name, {'user_tenant_type': user_type}, status=200)


def create_ticket(request, template_name='create-ticket.html'):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}')
    elif request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            tenant = get_tenant(request)
            new_issue = form.save(commit=False)  # create instance, but do not save
            new_issue.status = get_initial_status(get_env_type(new_issue.type.id))  # env_type field from issue type
            new_issue.key = f'{tenant.key}-{tenant.count + 1}'
            new_issue.tenant = tenant
            new_issue.save()  # create issue
            form.save_m2m()
            tenant.count += 1
            tenant.save()
            #return render(request, 'submit-ticket.html', status=200)
            return HttpResponseRedirect(f'submit')
        else:
            print(form.errors.as_data())
    else:
        form = IssueForm()
        tenant_type = get_session_tenant_type(request)
        if tenant_type == settings.CUST_TYPE:
            form.fields['type'].initial = 2
        elif tenant_type == settings.OPER_TYPE or tenant_type == settings.DEV_TYPE:
            form.fields['type'].initial = 1
        else:
            pass
        return render(request, template_name, {'form': form}, status=200)


def submit_ticket(request, template_name='submit-ticket.html'):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}')
    response = render(request, template_name, status=200)
    return response


def view_ticket(request, template_name='view-ticket.html'):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}')
    response = render(request, template_name, status=200)
    return response


def password_change(request, template_name='password-change.html'):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}?next={request.path}')
    elif request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect('password_change_success')
        else:
            print('dupa')
            print(form.errors.as_data())
            # messages.error(request, form.errors.as_data())
            # return render(request, template_name, status=200)
            variables = {
                'form': form
            }
            return render(template_name, {}, status=400)
    else:
        form = PasswordChangeForm(request.user)
        return render(request, template_name, {'form': form}, status=200)


def password_change_success(request, template_name='password-change-success.html'):
    print('dupa dupa')
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}')
    return render(request, template_name, status=200)


def password_reset(request, template_name='/password-reset/password-reset.html', email_template_name='password-reset/password-reset-email.html'):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['email']
            users = User.objects.filter(Q(email=data))
            if users.exists():
                for user in users:
                    email_data = {
                        'email': user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http'}
                    email = render_to_string(email_template_name, email_data)
                    try:
                        send_mail('', email, 'admin@example.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                return HttpResponseRedirect("password_reset_sent")
    else:
        form = PasswordResetForm()
        return render(request, template_name, {'form': form})


def logged_out(request, template_name='logged-out.html'):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse(home))
    return render(request, template_name, {}, status=200)


def bad_request(request, exception=None, template_name='errors/400.html'):
    return render(request, template_name, {}, status=400)


def unauthorized(request, exception=None, template_name='errors/401.html'):
    return render(request, template_name, {}, status=401)


def permission_denied(request, exception=None, template_name='error/403.html'):
    return render(request, template_name, {}, status=403)


def page_not_found(request, exception=None, template_name='errors/404.html'):
    return render(request, template_name, {}, status=404)


def internal_server_error(request, exception=None, template_name='error/500.html'):
    return render(request, template_name, {}, status=500)


def after_log_out(sender, user, request, **kwargs):
    print('log out')
    clear_tenant_session(user)


user_logged_out.connect(after_log_out)



#def login(request, template_name='login.html'):
#    if request.user.is_authenticated:
#        return HttpResponseRedirect(reverse(home))
#    return render(request, template_name, {}, status=200)

'''
def change_password(request):
    
'''