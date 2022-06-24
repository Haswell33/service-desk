from .models import Issue, IssueType, Label, User, Status, Resolution, Priority
from django.forms import ClearableFileInput, FileInput, FileField
from django.utils.translation import gettext_lazy as _
from django.forms import ValidationError
from django import forms

from tinymce.widgets import TinyMCE
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
        fields = ['title', 'type', 'priority', 'assignee', 'reporter', 'labels', 'description', 'attachments']
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

    def __init__(self, *args, **kwargs, ):
        super(TicketCreateForm, self).__init__(*args, **kwargs)
        #super(TicketCreateForm, self).__init__()
        #print(str(*args))
        #self.fields['attachments'] = forms.ChoiceField(label=u'attachments', choices='new', widget=ClearableFileInput(attrs={'multiple': True}), required=False)


    def clean(self):
        super(TicketCreateForm, self).clean()
        #if not (self.attachments):
        #     raise ValidationError("dont have a attachments file")
        print('clean')
        print(self.__dict__)
        #attachments = self.cleaned_data['attachments']
        #print(attachments)
        if self._errors:
            print(self._errors)



class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'priority', 'labels', 'description']
        labels = {
            'title': _('Title'),
            'priority': _('Priority'),
            'labels': _('Label/s'),
            'description': _('Description'),
        }
        help_texts = {
            'title': _('Summarize the ticket'),
        }
        widgets = {
            'priority': IconField,
            'labels': forms.SelectMultiple(attrs={'multiple': True})
        }
        limit_choices_to = {
            'priority': 5,
            'labels': 4,
        }

    #def __init__(self, *args, **kwargs):
    #    self.title = kwargs.pop('title', None)
    #    super(TicketUpdateForm, self).__init__(*args, **kwargs)


class TicketUpdateAssigneeForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['assignee']
        labels = {
            'assignee': _('Set assignee'),
        }
        widgets = {
            'assignee': IconField,
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













class TicketCreateForm2(forms.Form):
    title = forms.CharField()
    type = forms.ModelMultipleChoiceField(
        queryset=IssueType.objects.all(),
        required=True,
        widget=IconField(attrs={'multiple': 'true'}))
    priority = forms.ModelMultipleChoiceField(
        queryset=Priority.objects.all(),
        required=True,
        widget=IconField(attrs={'multiple': 'true'}))
    assignee = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=IconField)
    labels = forms.ModelMultipleChoiceField(
        queryset=Label.objects.all(),
        required=False)
    attachments = forms.ClearableFileInput(
        attrs={'multiple': True})
    description = forms.CharField(
        required=False,
        help_text='Describe the issue',
        widget=TinyMCE)
