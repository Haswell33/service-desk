from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, reverse, redirect
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.db.models.query_utils import Q
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from .models import Issue, IssueType, Priority, Status, Resolution, Label
from .forms import IssueForm, IssueFilterViewForm
from .utils import get_env_type, get_initial_status, get_active_tenant, active_tenant_session, get_active_tenant_session, tenant_session, clear_tenant_session, change_active_tenant, get_tenant_cookie_name, get_active_tenant_issues, get_board_columns_assocations, get_board_columns
from .context_processors import context_tenant_session

'''
def home(request, template_name='home.html'):
    
    else:
        if not active_tenant_session(request.user):
            context_tenant_session(request)
        return render(request, template_name, status=200)
'''

'''def view_ticket(request, template_name='ticket/ticket-view.html'):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}')
    response = render(request, template_name, status=200)
    print('dupa')
    return response'''


def check_get_request(self, request, view_name, *args, **kwargs):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}')
    elif request.COOKIES.get(get_tenant_cookie_name(request.user)) is None:
        return redirect('tenant_update')
    if not active_tenant_session(request.user):
        context_tenant_session(request)
    response = super(view_name, self).get(request, *args, **kwargs)
    response.status_code = 200
    return response


def after_logout(sender, user, request, **kwargs):
    clear_tenant_session(user)


def after_login(sender, user, request, **kwargs):
    if not tenant_session(user):
        context_tenant_session(request)

# Views


def create_ticket(request, template_name='ticket/ticket-create.html'):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}')
    elif request.COOKIES.get(get_tenant_cookie_name(request.user)) is None:
        return redirect('tenant_update')
    elif request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            tenant = get_active_tenant(request.user)
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
        if not active_tenant_session(request.user):
            context_tenant_session(request)
        tenant_session = get_active_tenant_session(request.user)
        if tenant_session.user_type == settings.CUST_TYPE:
            form.fields['type'].initial = 2
        elif tenant_session.user_type == settings.OPER_TYPE or tenant_session.user_type == settings.DEV_TYPE:
            form.fields['type'].initial = 1
        else:
            pass
        return render(request, template_name, {'form': form}, status=200)


def submit_ticket(request, template_name='ticket/ticket-submit.html'):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}')
    response = render(request, template_name, status=200)
    return response


class TicketDetailView(generic.detail.DetailView):
    model = Issue
    fields = ['title', 'key', 'status']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TicketBoardListView(generic.ListView):
    model = Issue
    paginate_by = 50
    context_object_name = 'tickets'
    template_name = 'home.html'

    def get_queryset(self):
        filter_assignee = self.request.GET.get('assignee', '')
        filter_reporter = self.request.GET.get('reporter', '')
        filter_ordering = self.request.GET.get('ordering', '')
        filter_ordering_type = self.request.GET.get('order_type', 'desc')
        tickets = get_active_tenant_issues(self.request.user, filter_assignee, filter_reporter, filter_ordering, filter_ordering_type)
        return tickets

    def get_context_data(self, **kwargs):
        context = super(TicketBoardListView, self).get_context_data(**kwargs)
        context.update({
            'board_columns_associations': get_board_columns_assocations(get_board_columns(self.request.user)),
            'users': User.objects.all(),
            'order_fields': {
                'Key': 'id',
                'Priority': 'priority',
                'Type': 'type',
                'Status': 'status',
                'Updated date': 'updated',
                'Created date': 'created',
                'Escalated': 'escalated',
                'Suspended': 'suspended',
            },
            'ordering_types': {
                'Ascending': 'asc',
                'Descending': 'desc'
            }
            # Issue._meta.get_fields()
        })
        return context

    def get(self, request, *args, **kwargs):
        return check_get_request(self, request, TicketBoardListView, *args, **kwargs)


class TicketFilterListView(generic.ListView):
    model = Issue
    paginate_by = 50
    context_object_name = 'tickets'
    template_name = 'ticket/ticket-filter.html'

    def get_queryset(self):
        filter_assignee = self.request.GET.get('assignee', '')
        filter_reporter = self.request.GET.get('reporter', '')
        filter_ordering = self.request.GET.get('ordering', '')
        filter_ordering_type = self.request.GET.get('order_type', 'desc')
        tickets = get_active_tenant_issues(self.request.user, filter_assignee, filter_reporter, filter_ordering, filter_ordering_type)
        return tickets

    def get_context_data(self, **kwargs):
        context = super(TicketFilterListView, self).get_context_data(**kwargs)
        context.update({
            'users': User.objects.all(),
            'form': IssueFilterViewForm(),
            'priorites': 'test',
            'statuses': Status.objects.all().exclude(name='All'),
            'resolutions': Resolution.objects.all(),
            'priorities': Priority.objects.all(),
            'types': IssueType.objects.all(),
            'labels': Label.objects.all(),
            'fields': {
                'Type': 'type',
                'Key': 'key',
                'Title': 'title',
                'Priority': 'priority',
                'Status': 'status',
                'Resolution': 'resolution',
                'Reporter': 'reporter',
                'Assignee': 'asignee',
                'Updated': 'updated',
                'Created': 'created'
            },
            'order_fields': {
                'Key': 'id',
                'Priority': 'priority',
                'Type': 'type',
                'Status': 'status',
                'Updated date': 'updated',
                'Created date': 'created',
                'Escalated': 'escalated',
                'Suspended': 'suspended',
            },
            'ordering_types': {
                'Ascending': 'asc',
                'Descending': 'desc'
            }
            # Issue._meta.get_fields()
        })
        return context

    def get(self, request, *args, **kwargs):
        return check_get_request(self, request, TicketFilterListView, *args, **kwargs)


def password_change(request, template_name='password/password-change.html'):
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


def password_change_success(request, template_name='password/password-change-success.html'):
    print('dupa dupa')
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}')
    return render(request, template_name, status=200)


def password_reset(request, template_name='password/password-reset.html', email_template_name='password/password-reset-email.html'):
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


@csrf_exempt
def tenant_update(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f'{settings.LOGIN_URL}')
    elif request.method == 'POST':
        tenant_id = request.POST.get('tenant_id')
        change_active_tenant(tenant_id, request.user)
    else:
        if not active_tenant_session(request.user):
            context_tenant_session(request)
        tenant_session = get_active_tenant_session(request.user)
        tenant_id = tenant_session.tenant.id
    response = redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    response.set_cookie(key=get_tenant_cookie_name(request.user), value=tenant_id)
    return response


user_logged_out.connect(after_logout)
user_logged_in.connect(after_login)

'''
def login(request):
    print('login')
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse(home))
    return render(request, {}, status=200)
'''