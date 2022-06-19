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


class IssueForm(forms.ModelForm):
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


class IssueFilterViewForm(forms.Form):
    assignee = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=IconField)
    reporter = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False)
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
        queryset=IssueType.objects.all(),
        required=False,
        widget=IconField)
    priority = forms.ModelMultipleChoiceField(
        queryset=Priority.objects.all(),
        required=False,
        widget=IconField)
    order_by_fields = forms.ChoiceField(
        choices=settings.ORDER_BY_FIELDS,
        required=False)
    order_by_type = forms.ChoiceField(
        choices=settings.ORDER_BY_TYPES,
        required=False)


# class CustomerIssueForm(forms.Form):
