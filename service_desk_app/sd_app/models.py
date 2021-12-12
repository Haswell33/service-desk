from django.db import models
import uuid
from datetime import datetime

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)


class Issue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular issue')
    summary = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.ForeignKey('IssuePriority', on_delete=models.SET_NULL, null=True)
    status = models.ForeignKey('IssueStatus', on_delete=models.SET_NULL, null=True)
    type = models.ForeignKey('IssueType', on_delete=models.SET_NULL, null=True)
    label = models.ForeignKey('IssueLabel', on_delete=models.SET_NULL, null=True)
    reported = models.ForeignKey('Users', on_delete=models.SET_NULL, null=True)
    creator = models.ForeignKey('Users', on_delete=models.SET_NULL, null=True)
    assigned = models.ForeignKey('Users', on_delete=models.SET_NULL, null=True)
    resolved = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=datetime.now())
    updated_date = models.DateTimeField(default=datetime.now())

    class Meta:
        ordering = ['due_back']

    def __str__(self):
        return f'{self.id} ({self.summary})'


class IssuePriority(models.Model):
    id = models.ForeignKey('Issue', on_delete=models.SET_NULL, null=True)
    '''
    priority_choices = ['Low', 'Normal', 'High', 'Critical']
    name = models.CharField(max_length=50, choices=priority_choices, help_text='Enter a name of priority')
    '''
    name = models.CharField(max_length=50, help_text='Enter a name of priority')
    description = models.TextField(help_text='Enter a description of priority')
    image = models.ImageField(max_length=50, help_text='Enter a link to image of priority')

    def __str__(self):  # for representation in admin site
        return self.name
