from .models import Issue, IssueType, Label, User, Status, Resolution, Priority
from django.forms import ClearableFileInput
from django.utils.translation import gettext_lazy as _
from django import forms
from django.conf import settings


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
        model = Issue
        fields = ['title', 'type', 'priority', 'assignee', 'labels', 'description', 'attachments', 'status']
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
            'assignee': IconField,
            'attachments': ClearableFileInput(attrs={'multiple': True}),
        }

        # def __init__(self, request):



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
        queryset=Status.objects.all().exclude(name='All'),
        required=False)
    resolution = forms.ModelMultipleChoiceField(
        queryset=Resolution.objects.all(),
        required=False)
    label = forms.ModelMultipleChoiceField(
        queryset=Label.objects.all(),
        required=False)
    type = forms.ModelMultipleChoiceField(
        queryset=IssueType.objects.all(),
        required=False,
        widget=IconField(attrs={'multiple': 'true', 'icon': 'dupa'}))
    priority = forms.ModelMultipleChoiceField(
        queryset=Priority.objects.all(),
        required=False,
        widget=IconField(attrs={'multiple': 'true'}))


# class CustomerIssueForm(forms.Form):
