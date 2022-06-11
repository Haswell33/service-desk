from django.http import HttpResponseRedirect
from django.http.cookie import SimpleCookie
from django.shortcuts import render, reverse
from django.conf import settings
from .models import Tenant, Status, IssueType, Issue
from .forms import IssueForm
from .utils import get_session_tenant_type, get_env_type, get_initial_status, get_tenant


def home(request, template_name='home.html'):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}')
    issues = Issue.objects.all()
    response = render(request, template_name, {"issues": issues},  status=200)
    response.set_cookie(key='active_tenant_id', value=1)
    return response
    # return render(request, template_name, {'user_tenant_type': user_type}, status=200)


def create_ticket(request, template_name='create-ticket.html'):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}')
    elif request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            tenant = get_tenant(request)
            new_issue = form.save(commit=False)  # create instance, but do not save
            env_type = get_env_type(new_issue.type.id)  # env_type field from issue type
            new_issue.status = get_initial_status(env_type)
            new_issue.key = f'{tenant.key}-{tenant.count + 1}'
            new_issue.tenant = tenant
            print(new_issue.description)
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


def unauthorized(request, exception=None, template_name='errors/401.html'):
    return render(request, template_name, {}, status=401)


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