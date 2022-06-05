from .models import Issue
from django.forms import ClearableFileInput
from django.utils.translation import gettext_lazy as _
from django import forms


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'type', 'priority', 'assignee', 'label', 'description', 'attachments']
        labels = {
            'title': _('Title'),
            'type': _('Issue type'),
            'priority': _('Priority'),
            'assignee': _('Assignee'),
            'label': _('Label/s'),
            'description': _('Description'),
            'attachments': _('Attach a file'),
        }
        help_texts = {
            'type': _('Take your type'),
        }
        widgets = {
            'file': ClearableFileInput(attrs={'multiple': True}),
        }
