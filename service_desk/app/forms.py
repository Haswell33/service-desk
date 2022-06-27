from django.forms import ClearableFileInput, FileInput, FileField, MultiValueField
from django.utils.translation import gettext_lazy as _
from django import forms
from tinymce.widgets import TinyMCE
from .models import Ticket, Type, Label, User, Status, Resolution, Priority, Comment
from .utils import get_initial_type, get_type_options, get_user_field_options_by_active_tenant, get_user_field_options_by_ticket, user_is_customer, get_available_statuses


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


class ModelIconChoiceField(forms.ModelChoiceField):
    def __init__(self, my_attr, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_attr = my_attr


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
        self.fields['type'] = forms.ModelChoiceField(
            queryset=get_type_options(self.request.user),
            initial=get_initial_type(self.request.user),
            required=True,
            widget=IconField)
        if user_is_customer(self.request.user):
            self.fields.pop('assignee')
        else:
            self.fields['assignee'] = forms.ModelChoiceField(
                queryset=get_user_field_options_by_active_tenant(self.request.user),
                widget=IconField)


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
        instance = kwargs.pop('instance')
        super(TicketEditAssigneeForm, self).__init__(*args, **kwargs)
        self.fields['assignee'] = forms.ModelChoiceField(
            queryset=get_user_field_options_by_ticket(instance),
            initial=instance.assignee,
            required=False,
            widget=IconField)


class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


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
        widget=IconField(attrs={'multiple': 'true', 'icon': 'dupa'}))
    priority = forms.ModelMultipleChoiceField(
        queryset=Priority.objects.all(),
        required=False,
        widget=IconField(attrs={'multiple': 'true'}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(TicketFilterViewForm, self).__init__(*args, **kwargs)
        user_field_options = get_user_field_options_by_active_tenant(self.request.user)
        self.fields['reporter'] = forms.ModelChoiceField(
            queryset=user_field_options,
            required=False,
            widget=IconField)
        self.fields['assignee'] = forms.ModelChoiceField(
            queryset=user_field_options,
            required=False,
            widget=IconField)
        self.fields['type'] = forms.ModelChoiceField(
            queryset=get_type_options(self.request.user),
            required=False,
            widget=IconField)
        self.fields['status'] = forms.ModelChoiceField(
            queryset=get_available_statuses(self.request.user),
            required=False)
