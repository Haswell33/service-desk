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
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import FormMixin
from django.db.models.query_utils import Q
from django.views import generic
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.urls.exceptions import NoReverseMatch
from .models import Ticket, TransitionAssociation, Attachment, Comment, Status
from .forms import TicketCreateForm, TicketFilterViewForm, TicketEditAssigneeForm, TicketEditForm, TicketCommentForm
from .utils import get_env_type, get_initial_status, get_active_tenant, active_tenant_session, get_active_tenant_session, tenant_session, clear_tenant_session, change_active_tenant, get_tenant_cookie_name, get_active_tenant_tickets, get_board_columns_assocations, get_board_columns, filter_tickets, order_tickets, get_transition_options, convert_query_dict_to_dict, set_ticket_status, set_ticket_assignee, create_ticket, update_ticket, set_ticket_suspend, add_attachment, delete_attachment, add_relation, delete_relation, get_allow_tickets_to_relate, add_comment, delete_comment, edit_comment, get_audit_logs, has_access_to_ticket
from .context_processors import context_tenant_session


def validate_get_request(self, request, view_name, *args, **kwargs):
    if not request.user.is_authenticated:
        return login_page(request.path)
    elif request.COOKIES.get(get_tenant_cookie_name(request.user)) is None:
        return redirect('tenant_update')
    if not active_tenant_session(request.user):  # check if any record in tenant_session is stored with active state
        context_tenant_session(request)  # assign active tenant/s based on membership to groups
    response = super(view_name, self).get(request, *args, **kwargs)
    response.status_code = 200
    return response


def code_403(request):
    return render(request, 'errors/403.html', {}, status=403)


def code_405(request):
    return render(request, 'errors/405.html', {}, status=405)


def login_page(path):
    if not path == '/':
        return HttpResponseRedirect(f'{settings.LOGIN_URL}?next={path}')
    else:
        return HttpResponseRedirect(settings.LOGIN_URL)


def after_logout(sender, user, request, **kwargs):
    clear_tenant_session(user)


def after_login(sender, user, request, **kwargs):
    if not tenant_session(user):
        context_tenant_session(request)


user_logged_out.connect(after_logout)
user_logged_in.connect(after_login)

# Views


class TicketCreateView(SuccessMessageMixin, generic.CreateView):
    model = Ticket
    form_class = TicketCreateForm
    template_name = '/ticket/ticket-create.html'

    def get_initial(self):
        initial = super(TicketCreateView, self).get_initial()
        initial['reporter'] = self.request.user
        return initial

    def get_form_kwargs(self):
        kwargs = super(TicketCreateView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def get_success_url(self, **kwargs):
        return reverse_lazy('view_ticket', args=(self.object.slug,))

    def get_success_message(self, cleaned_data):
        return f'Ticket <strong>{self.object.key}</strong> was created successfully'

    def form_valid(self, form):
        create_ticket(form, self.request)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect(self.request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

    def get(self, request, *args, **kwargs):
        return validate_get_request(self, request, TicketCreateView, *args, **kwargs)


class TicketDetailView(FormMixin, generic.detail.DetailView):  # Detail view for ticket
    model = Ticket
    form_class = TicketEditAssigneeForm

    def get_form_kwargs(self):
        kwargs = super(TicketDetailView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request,
            'instance': self.object
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'transitions': get_transition_options(self.object),
            'audit_logs': get_audit_logs(self.object),
            'available_tickets_to_relate': get_allow_tickets_to_relate(self.request.user, self.get_object()),
            'form_update': TicketEditForm(instance=self.object),
            'form_update_assignee': self.get_form(),
            'form_comment': TicketCommentForm()
        })
        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_page(request.path)
        elif not has_access_to_ticket(request.user, self.get_object()):
            return code_403(request)
        return validate_get_request(self, request, TicketDetailView, *args, **kwargs)


class TicketDetailEdit(generic.UpdateView):
    model = Ticket
    fields = ['title', 'priority', 'description', 'labels']

    def form_invalid(self, form):
        print(form.errors.as_data())
        return HttpResponse('invalid form')

    def get(self, request, *args, **kwargs):
        return code_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        form = TicketEditForm(request.POST or None, instance=ticket)
        ticket_updated = update_ticket(form, request)
        if ticket_updated:
            messages.success(request, f'Ticket <strong>{ticket_updated.key}</strong> has been updated')
        elif ticket_updated is None:
            messages.info(request, f'No changes detected in <strong>{ticket.key}</strong>')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketDetailEditStatus(generic.UpdateView):
    model = Ticket
    fields = ['status']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'transitions': get_transitions(self.object)  # transition associations
        })
        return context

    def get(self, request, *args, **kwargs):
        return code_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not has_access_to_ticket(request.user, ticket):
            return code_403(request)
        super().post(request, *args, **kwargs)
        context_transition_associations = self.get_context_data().get('transitions')
        try:
            transition_association = TransitionAssociation.objects.get(id=request.POST.get('transition'))
            result = set_ticket_status(transition_association, context_transition_associations, ticket, request)
            if isinstance(result, Status):
                messages.success(request, f'Status of <strong>{ticket.key}</strong> has been changed to <strong>{result}</strong>')
            else:
                messages.error(request, result)
        except TransitionAssociation.DoesNotExist:
            messages.error(request, f'Transition in <strong>{ticket}</strong> not exist')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketDetailEditAssignee(generic.UpdateView):
    model = Ticket
    fields = ['assignee']

    def get(self, request, *args, **kwargs):
        return code_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not has_access_to_ticket(request.user, ticket):
            return code_403(request)
        user_id = request.POST.get('assignee')
        try:
            if user_id is None or user_id == '':
                user = None
            else:
                user = User.objects.get(id=request.POST.get('assignee'))
            result = set_ticket_assignee(user, ticket, request)
            if isinstance(result, User):
                messages.success(request, f'Ticket has been assigned to <strong>{result}</strong>')
            elif user is None:
                messages.success(request, result)
            else:
                messages.error(request, result)
        except User.DoesNotExist:
            messages.error(request, f'Selected user not exist')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketDetailEditSuspend(generic.UpdateView):
    model = Ticket
    fields = ['suspended']

    def get(self, request, *args, **kwargs):
        return code_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not has_access_to_ticket(request.user, ticket):
            return code_403(request)
        ticket_updated = set_ticket_suspend(ticket, request)
        if ticket_updated.suspended is True:
            messages.success(request, f'Ticket <strong>{ticket_updated}</strong> has been suspended')
        else:
            messages.success(request, f'Ticket <strong>{ticket_updated}</strong> has been unsuspended')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketDetailAddAttachment(generic.UpdateView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        return code_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not has_access_to_ticket(request.user, ticket):
            return code_403(request)
        files = request.FILES.getlist('attachments')
        if files:
            for file in files:
                attachment = add_attachment(file, ticket, request)
                messages.success(request, f'Attachment <strong>{attachment}</strong> has been uploaded to <strong>{ticket.key}</strong>')
        else:
            messages.info(request, f'No new files uploaded to <strong>{ticket.key}</strong>')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketDetailDeleteAttachment(generic.DeleteView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        return code_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not has_access_to_ticket(request.user, ticket):
            return code_403(request)
        attachment_id = request.POST.get('attachment')
        try:
            attachment = Attachment.objects.get(id=attachment_id)
            result = delete_attachment(ticket, attachment, request)
            if result is True:
                messages.success(request, f'Attachment <strong>{attachment.filename}</strong> has been deleted from <strong>{ticket.key}</strong>')
            else:
                messages.error(request, result)
        except Attachment.DoesNotExist:
            messages.error(request, f'Attachment with value <strong>{attachment_id}</strong> not exist')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketDetailAddRelation(generic.UpdateView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        return code_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not has_access_to_ticket(request.user, ticket):
            return code_403(request)
        tickets_to_relate = request.POST.getlist('relations')
        if tickets_to_relate:
            for ticket_to_relate in tickets_to_relate:
                result = add_relation(ticket, ticket_to_relate, request)
                if isinstance(result, Ticket):
                    messages.success(request, f'Relation between <strong>{ticket.key}</strong> and <strong>{result}</strong> has been created')
                else:
                    messages.error(request, result)
        else:
            messages.info(request, f'No ticket has been selected to create relation with <strong>{ticket.key}</strong>')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketDetailDeleteRelation(generic.UpdateView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        return code_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not has_access_to_ticket(request.user, ticket):
            return code_403(request)
        relation_id = request.POST.get('relation')
        try:
            relation = Ticket.objects.get(id=relation_id)
            result = delete_relation(ticket, relation, request)
            if result is True:
                messages.success(request, f'Relation between <strong>{ticket}</strong> and <strong>{relation}</strong> has been deleted')
            else:
                messages.error(request, result)
        except Ticket.DoesNotExist:
            messages.error(request, f'Relation with value <strong>{relation_id}</strong> not exist')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketDetailAddComment(generic.UpdateView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        return code_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not has_access_to_ticket(request.user, ticket):
            return code_403(request)
        comment = request.POST.get('content')
        if comment:
            result = add_comment(ticket, comment, request)
            if isinstance(result, Comment):
                messages.success(request, f'Comment in <strong>{ticket.key}</strong> has been added')
            else:
                messages.error(request, result)
        else:
            messages.info(request, f'Comment not exist in <strong>{ticket.key}</strong>')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketDetailDeleteComment(generic.UpdateView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        return code_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not has_access_to_ticket(request.user, ticket):
            return code_403(request)
        comment_id = request.POST.get('comment')
        try:
            comment = Comment.objects.get(id=comment_id)
            result = delete_comment(ticket, comment, request)
            if result is True:
                messages.success(request, f'Comment from <strong>{ticket}</strong> has been deleted')
            else:
                messages.error(request, result)
        except Comment.DoesNotExist:
            messages.error(request, f'Comment in <strong>{ticket}</strong> not exist')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketDetailEditComment(generic.UpdateView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        return code_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not has_access_to_ticket(request.user, ticket):
            return code_403(request)
        comment_id = request.POST.get('comment')
        content = request.POST.get('content')
        try:
            comment = Comment.objects.get(id=comment_id)
            result = edit_comment(ticket, comment, content, request)
            if isinstance(result, Comment):
                messages.success(request, f'Comment in <strong>{ticket.key}</strong> has been updated')
            else:
                messages.error(request, result)
        except Comment.DoesNotExist:
            messages.error(request, f'Comment in <strong>{ticket}</strong> not exist')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketBoardListView(generic.ListView):
    model = Ticket
    context_object_name = 'tickets'
    template_name = 'home.html'

    def get_queryset(self):
        tickets = get_active_tenant_tickets(self.request.user, True)
        return tickets

    def get_context_data(self, **kwargs):
        context = super(TicketBoardListView, self).get_context_data(**kwargs)
        context.update({
            'board_columns_associations': get_board_columns_assocations(get_board_columns(self.request.user)),
            'users': User.objects.all(),
            'fields': settings.ORDER_BY_FIELDS
        })
        return context

    def get(self, request, *args, **kwargs):
        return validate_get_request(self, request, TicketBoardListView, *args, **kwargs)


class TicketFilterListView(FormMixin, generic.ListView):
    model = Ticket
    context_object_name = 'tickets'
    form_class = TicketFilterViewForm
    template_name = 'ticket/ticket-filter.html'
    ordering = ['key']

    def get_form_kwargs(self):
        kwargs = super(TicketFilterListView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def get_queryset(self):
        filters = {
            'assignee': self.request.GET.get('assignee', ''),
            'reporter': self.request.GET.get('reporter', ''),
            'status': self.request.GET.getlist('status', ''),
            'resolution': self.request.GET.getlist('resolution', ''),
            'labels': self.request.GET.getlist('label', ''),
            'type': self.request.GET.getlist('type', ''),
            'priority': self.request.GET.getlist('priority', '')
        }
        tickets = get_active_tenant_tickets(self.request.user, False)
        tickets = filter_tickets(tickets, filters)
        if self.request.GET.get('ordering'):  # if any ordering provided in request
            tickets = order_tickets(tickets, self.get_ordering())
        return tickets

    def get_context_data(self, **kwargs):
        context = super(TicketFilterListView, self).get_context_data(**kwargs)
        context.update({
            'form': self.get_form(),
            'fields': settings.ORDER_BY_FIELDS,
            'curr_ordering': self.request.GET.get('ordering'),
            'curr_selected': convert_query_dict_to_dict(self.request.GET)
        })
        return context

    def get_ordering(self):
        return self.request.GET.get('ordering', 'key')

    def get(self, request, *args, **kwargs):
        return validate_get_request(self, request, TicketFilterListView, *args, **kwargs)


def password_change(request, template_name='password/password-change.html'):
    if not request.user.is_authenticated:
        return login_page(request.path)
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
        return login_page(request.path)
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
                        send_mail('', email, 'admin@example.com', [user.email])
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


def method_not_allowed(request, exception=None, template_name='errors/405.html'):
    return render(request, template_name, {}, status=405)


def internal_server_error(request, exception=None, template_name='error/500.html'):
    return render(request, template_name, {}, status=500)


@csrf_exempt
def tenant_update(request):
    if not request.user.is_authenticated:
        return login_page(request.path)
    elif request.method == 'POST':
        tenant_id = request.POST.get('tenant_id')
        change_active_tenant(tenant_id, request.user)
    else:
        if not active_tenant_session(request.user):
            context_tenant_session(request)
        tenant_session = get_active_tenant_session(request.user)
        tenant_id = tenant_session.tenant.id
    try:
        response = redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
        response.set_cookie(key=get_tenant_cookie_name(request.user), value=tenant_id)
        return response
    except NoReverseMatch:
        response = redirect('home')
        response.set_cookie(key=get_tenant_cookie_name(request.user), value=tenant_id)
        return response


'''
def login(request):
    print('login')
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse(home))
    return render(request, {}, status=200)
'''

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

'''
def create_ticket(request, template_name='ticket/ticket-create.html'):
    if not request.user.is_authenticated:
        return login_page(request.path)
    elif request.COOKIES.get(get_tenant_cookie_name(request.user)) is None:
        return redirect('tenant_update')
    elif request.method == 'POST':
        form = TicketCreateForm(request.POST)
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
        form = TicketCreateForm()
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
'''


'''

ticket create view
def get_context_data(self, **kwargs):
        context = super(TicketCreateView, self).get_context_data(**kwargs)
        context.update({
            'form': self.get_form()
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(TicketCreateView, self).get_form_kwargs()
        kwargs['reporter'] = self.request.user
        return kwargs'''

'''
def submit_ticket(request, template_name='ticket/ticket-submit.html'):
    if not request.user.is_authenticated:
        return login_page(request.path)
    response = render(request, template_name, status=200)
    return response
'''