from django.utils.translation import gettext_lazy as _
from django import forms
from .models import Ticket, Type, Label, User, Status, Resolution, Priority, Comment
from .utils import type_manager, tenant_manager, status_manager


class IconField(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            option['attrs']['icon'] = value.instance.icon
        return option


class EmptyDefault(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value == '':
            option['attrs']['style'] = 'display: none'
        return option


class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'type', 'priority', 'assignee', 'reporter', 'labels', 'description', ]  # 'attachments' field is added in separate way
        labels = {
            'title': _('Title'),
            'type': _('Type'),
            'priority': _('Priority'),
            'assignee': _('Assignee'),
            'labels': _('Label/s'),
            'description': _('Description'),
            'attachments': _('Attach a file'),
        }
        help_texts = {
            'title': _('Summarize the ticket'),
        }
        id_label = {
            'type': _('id_type'),
        }
        widgets = {
            'type': IconField,
            'priority': IconField,
            'assignee': IconField
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(TicketCreateForm, self).__init__(*args, **kwargs)
        user = self.request.user
        self.fields['type'] = forms.ModelChoiceField(
            queryset=type_manager.get_type_options(user),
            initial=type_manager.get_initial_type(user),
            required=True,
            widget=IconField)
        if user.is_customer:
            self.fields.pop('assignee')
        else:
            self.fields['assignee'] = forms.ModelChoiceField(
                queryset=tenant_manager.get_active_tenant_session(user).get_user_field_options(),
                widget=IconField,
                required=False)


class TicketEditForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'priority', 'labels', 'description']
        labels = {
            'title': _('Title'),
            'priority': _('Priority'),
            'labels': _('Label/s'),
            'description': _('Description'),
        }
        widgets = {
            'priority': IconField,
            'labels': forms.SelectMultiple(attrs={'multiple': True}),
        }


class TicketEditAssigneeForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['assignee']
        labels = {
            'assignee': _('Set assignee'),
        }
        widgets = {
            'assignee': IconField,
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        ticket = kwargs.pop('ticket')
        super(TicketEditAssigneeForm, self).__init__(*args, **kwargs)
        self.fields['assignee'] = forms.ModelChoiceField(
            queryset=ticket.get_user_field_options(),
            initial=ticket.assignee,
            required=False,
            widget=IconField)


class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class TicketCloneForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['type']
        labels = {
            'type': _('Select type of cloned ticket'),
        }
        widgets = {
            'type': IconField,
        }


class TicketFilterViewForm(forms.Form):
    assignee = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=IconField)
    reporter = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=IconField)
    status = forms.ModelMultipleChoiceField(
        queryset=Status.objects.all(),
        required=False)
    resolution = forms.ModelMultipleChoiceField(
        queryset=Resolution.objects.all(),
        required=False)
    label = forms.ModelMultipleChoiceField(
        queryset=Label.objects.all(),
        required=False)
    type = forms.ModelMultipleChoiceField(
        queryset=Type.objects.all(),
        required=False,
        widget=IconField(attrs={'multiple': 'true'}))
    priority = forms.ModelMultipleChoiceField(
        queryset=Priority.objects.all(),
        required=False,
        widget=IconField(attrs={'multiple': 'true'}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(TicketFilterViewForm, self).__init__(*args, **kwargs)
        user_field_options = tenant_manager.get_active_tenant_session(self.request.user).get_user_field_options()
        self.fields['reporter'] = forms.ModelChoiceField(
            queryset=user_field_options,
            required=False,
            widget=IconField)
        self.fields['assignee'] = forms.ModelChoiceField(
            queryset=user_field_options,
            required=False,
            widget=IconField)
        self.fields['type'] = forms.ModelChoiceField(
            queryset=type_manager.get_type_options(self.request.user),
            required=False,
            widget=IconField)
        self.fields['status'] = forms.ModelChoiceField(
            queryset=status_manager.get_available_status_list(self.request.user),
            required=False)
