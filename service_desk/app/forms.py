from .models import Issue, IssueType
from django.forms import ClearableFileInput
from django_quill.forms import QuillFormField
from django.utils.translation import gettext_lazy as _
from django import forms


class IconField(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            option['attrs']['icon'] = value.instance.icon
        return option


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'type', 'priority', 'assignee', 'label', 'description', 'attachments', 'status']
        labels = {
            'title': _('Title'),
            'type': _('Type'),
            'priority': _('Priority'),
            'assignee': _('Assignee'),
            'label': _('Label/s'),
            'description': _('Description'),
            'attachments': _('Attach a file'),
        }
        help_texts = {
            'title': _('Summarize the ticket'),
        }
        id_label = {
            'type': _('id_dupa'),
        }
        widgets = {
            'type': IconField,
            'priority': IconField,
            'assignee': IconField,
            'attachments': ClearableFileInput(attrs={'multiple': True}),
        }


# class CustomerIssueForm(forms.Form):
