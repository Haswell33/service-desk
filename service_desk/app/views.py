from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, reverse, redirect
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import FormMixin
from django.db.models.query_utils import Q
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.urls.exceptions import NoReverseMatch
from .models import Ticket, TransitionAssociation, Attachment, Comment, Status
from .forms import TicketCreateForm, TicketFilterViewForm, TicketEditAssigneeForm, TicketEditForm, TicketCommentForm, TicketCloneForm, User
from .utils import tenant_manager, board_manager, ticket_manager, utils
from .context_processors import context_tenant_session


def validate_get_request(self, request, view_name, tenant_check=False, *args, **kwargs):
    if not request.user.is_authenticated:
        return login_page(request.path)
    elif request.COOKIES.get(tenant_manager.get_tenant_cookie_name(request.user)) is None:
        return redirect('tenant_update', f'?tenant_check={tenant_check}')
    if not tenant_manager.active_session_exists(request.user):  # check if any record in tenant_session is stored with active state
        context_tenant_session(request)  # assign active tenant/s based on membership to groups
    response = super(view_name, self).get(request, *args, **kwargs)
    response.status_code = 200
    return response


def error_no_tenant(request):
    return render(request, 'errors/no-tenant.html', {}, status=403)


def error_403(request):
    return render(request, 'errors/403.html', {}, status=403)


def error_404(request):
    return render(request, 'errors/404.html', {}, status=404)


def error_405(request):
    return render(request, 'errors/405.html', {}, status=405)


def login_page(path):
    if not path == '/':
        return HttpResponseRedirect(f'{settings.LOGIN_URL}?next={path}')
    else:
        return HttpResponseRedirect(settings.LOGIN_URL)


def after_logout(sender, user, request, **kwargs):
    tenant_manager.clear_tenant_session(user)


def after_login(sender, user, request, **kwargs):
    if not tenant_manager.tenant_session(user):
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
        Ticket.create_ticket(form, self.request.user, self.request.FILES.getlist('attachments'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect(self.request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

    def get(self, request, *args, **kwargs):
        return validate_get_request(self, request, TicketCreateView, tenant_check=True, *args, **kwargs)


class TicketDetailView(FormMixin, generic.detail.DetailView):  # Detail view for ticket
    model = Ticket
    form_class = TicketEditAssigneeForm

    def get_form_kwargs(self):
        kwargs = super(TicketDetailView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request,
            'ticket': self.object
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket = self.object
        user = self.request.user
        context.update({
            'transitions': ticket.get_transition_options(user),
            'available_tickets_to_relate': ticket.get_relation_options(user),
            'allow_to_suspend': ticket.permission_to_suspend(user),
            'allow_to_assign': ticket.permission_to_assign(user),
            'allow_to_clone': ticket.permission_to_clone(user),
            'audit_logs': ticket.get_audit_logs(),
            'form_update': TicketEditForm(instance=ticket),
            'form_comment': TicketCommentForm(),
            'form_clone_ticket': TicketCloneForm(),
            'form_update_assignee': self.get_form()
        })
        return context

    def get(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not request.user.is_authenticated:
            return login_page(request.path)
        elif not ticket.permission_to_open(request.user):
            return error_403(request)
        return validate_get_request(self, request, TicketDetailView, tenant_check=True, *args, **kwargs)


class TicketDetailEdit(generic.UpdateView):
    model = Ticket
    fields = ['title', 'priority', 'description', 'labels']

    def form_invalid(self, form):
        print(form.errors.as_data())
        return HttpResponse('invalid form')

    def get(self, request, *args, **kwargs):
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        form = TicketEditForm(request.POST or None, instance=ticket)
        ticket_updated = ticket.update_ticket(form)
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
        ticket = self.object
        context.update({
            'transitions': ticket.get_transition_options(self.request.user)
        })
        return context

    def get(self, request, *args, **kwargs):
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user):
            return error_403(request)
        super().post(request, *args, **kwargs)
        context_transition_associations = self.get_context_data().get('transitions')
        try:
            transition_association = TransitionAssociation.objects.get(id=request.POST.get('transition'))
            result = ticket.set_status(transition_association, context_transition_associations)
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
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user) or not ticket.permission_to_assign(request.user):
            return error_403(request)
        user_id = request.POST.get('assignee')
        try:
            if user_id is None or user_id == '':
                user = None
            else:
                user = User.objects.get(id=request.POST.get('assignee'))
            result = ticket.set_assignee(user)
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
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user) or not ticket.permission_to_suspend(request.user):
            return error_403(request)
        result = ticket.set_suspended()
        if result.suspended is True:
            messages.success(request, f'Ticket <strong>{result}</strong> has been suspended')
        else:
            messages.success(request, f'Ticket <strong>{result}</strong> has been unsuspended')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketDetailAddAttachment(generic.UpdateView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user):
            return error_403(request)
        files = request.FILES.getlist('attachments')
        if files:
            for file in files:
                result = ticket.add_attachment(file)
                messages.success(request, f'Attachment <strong>{result}</strong> has been uploaded to <strong>{ticket}</strong>')
        else:
            messages.info(request, f'No new files uploaded to <strong>{ticket.key}</strong>')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketDetailDeleteAttachment(generic.DeleteView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user):
            return error_403(request)
        attachment_id = request.POST.get('attachment')
        try:
            attachment = Attachment.objects.get(id=attachment_id)
            result = ticket.delete_attachment(attachment, request.user)
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
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user):
            return error_403(request)
        tickets_to_relate = request.POST.getlist('relations')
        if tickets_to_relate:
            for ticket_to_relate in tickets_to_relate:
                result = ticket.add_relation(ticket_to_relate, self.request.user)
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
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user):
            return error_403(request)
        relation_id = request.POST.get('relation')
        try:
            relation = Ticket.objects.get(id=relation_id)
            result = ticket.delete_relation(relation, request.user)
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
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user):
            return error_403(request)
        comment_content = request.POST.get('content')
        if comment_content:
            result = ticket.add_comment(comment_content)
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
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user):
            return error_403(request)
        comment_id = request.POST.get('comment')
        try:
            comment = Comment.objects.get(id=comment_id)
            result = ticket.delete_comment(comment, request.user)
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
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open(request.user):
            return error_403(request)
        comment_id = request.POST.get('comment')
        content = request.POST.get('content')
        try:
            comment = Comment.objects.get(id=comment_id)
            result = ticket.edit_comment(comment, content, request.user)
            if isinstance(result, Comment):
                messages.success(request, f'Comment in <strong>{ticket.key}</strong> has been updated')
            else:
                messages.error(request, result)
        except Comment.DoesNotExist:
            messages.error(request, f'Comment in <strong>{ticket}</strong> not exist')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketDetailClone(generic.UpdateView):
    model = Ticket

    def get(self, request, *args, **kwargs):
        return error_405(request)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not ticket.permission_to_open_ticket(request.user) or not ticket.permission_to_clone(request.user):
            return error_403(request)
        type_id = request.POST.get('type')
        if type_id:
            result = ticket.clone_ticket(ticket, type_id)
            if isinstance(result, Ticket):
                messages.success(request, f'Ticket <strong>{ticket}</strong> has been cloned to <strong>{result}</strong>')
                return HttpResponseRedirect(reverse('view_ticket', args=[result.slug]))
            else:
                messages.error(request, result)
        else:
            messages.info(request, f'Selected type not exist')
        return HttpResponseRedirect(reverse('view_ticket', args=[ticket.slug]))


class TicketBoardListView(generic.ListView):
    model = Ticket
    context_object_name = 'tickets'
    template_name = 'home.html'

    def get_queryset(self):
        tickets = tenant_manager.get_active_tenant_tickets(self.request.user, True)
        return tickets

    def get_context_data(self, **kwargs):
        context = super(TicketBoardListView, self).get_context_data(**kwargs)
        context.update({
            'board_columns_associations': board_manager.get_board_columns_associations(board_manager.get_board_columns(self.request.user)),
            'users': User.objects.all(),
            'fields': settings.ORDER_BY_FIELDS
        })
        return context

    def get(self, request, *args, **kwargs):
        return validate_get_request(self, request, TicketBoardListView, tenant_check=True, *args, **kwargs)


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
        tickets = tenant_manager.get_active_tenant_tickets(self.request.user)
        tickets = ticket_manager.filter_tickets(tickets, filters)
        if self.request.GET.get('ordering'):  # if any ordering provided in request
            tickets = ticket_manager.order_tickets(tickets, self.get_ordering())
        return tickets

    def get_context_data(self, **kwargs):
        context = super(TicketFilterListView, self).get_context_data(**kwargs)
        context.update({
            'form': self.get_form(),
            'fields': settings.ORDER_BY_FIELDS,
            'curr_ordering': self.request.GET.get('ordering'),
            'curr_selected': utils.convert_query_dict_to_dict(self.request.GET)
        })
        return context

    def get_ordering(self):
        return self.request.GET.get('ordering', 'key')

    def get(self, request, *args, **kwargs):
        return validate_get_request(self, request, TicketFilterListView, tenant_check=True, *args, **kwargs)


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
        return HttpResponseRedirect(reverse('home'))
    return render(request, template_name, {}, status=200)


def bad_request(request, template_name='errors/400.html'):
    return render(request, template_name, {}, status=400)


def unauthorized(request, template_name='errors/401.html'):
    return render(request, template_name, {}, status=401)


def permission_denied(request, template_name='error/403.html'):
    return render(request, template_name, {}, status=403)


def page_not_found(request, template_name='errors/404.html'):
    return render(request, template_name, {}, status=404)


def method_not_allowed(request, template_name='errors/405.html'):
    return render(request, template_name, {}, status=405)


def internal_server_error(request, template_name='error/500.html'):
    return render(request, template_name, {}, status=500)


@csrf_exempt
def tenant_update(request, tenant_check=False):
    if not request.user.is_authenticated:
        return login_page(request.path)
    elif request.method == 'POST':
        tenant_session = tenant_manager.get_active_tenant_session(request.user)
        tenant_id = request.POST.get('tenant_id')
        tenant_session.change_active(tenant_id, request.user)
    else:
        if not tenant_manager.active_session_exists(request.user):
            context_tenant_session(request)
        tenant_session = tenant_manager.get_active_tenant_session(request.user)
        if not tenant_session and tenant_check:
            return error_no_tenant(request)
        tenant_id = tenant_session.tenant.id
    try:
        response = redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
        response.set_cookie(key=tenant_manager.get_tenant_cookie_name(request.user), value=tenant_id)
        return response
    except NoReverseMatch:
        response = redirect('home')
        response.set_cookie(key=tenant_manager.get_tenant_cookie_name(request.user), value=tenant_id)
        return response
