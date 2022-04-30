from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib import admin
from django.contrib.auth.models import User, Group, User
from django.conf import settings
from crum import get_current_user
from datetime import datetime
from . import utils


class SLA(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    reaction_time = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(43200)], help_text='Time to reaction in minutes before escalation')
    resolve_time = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(43200)], help_text='Time to resolve in minutes before escalation')
    hour_range = models.CharField(max_length=5)

    class Meta:
        db_table = 'tenant_sla'
        ordering = ['id']


class Workflow(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    pattern = models.TextField(help_text='XML file to descript workflow')

    class Meta:
        db_table = 'tenant_workflow'


class Tenant(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    sla = models.ForeignKey(SLA, on_delete=models.CASCADE)
    workflow_operator = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='%(class)_workflow_operator', help_text='Workflow scheme for Service Desk space')
    workflow_developer = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='%(class)_workflow_developer', help_text='Workflow scheme for Developer space')
    customers = models.ForeignKey(Group, related_name='%(class)_customer', on_delete=models.DO_NOTHING)
    operators = models.ForeignKey(Group, related_name='%(class)_operator', on_delete=models.DO_NOTHING)
    developers = models.ForeignKey(Group, related_name='%(class)_developer', on_delete=models.DO_NOTHING)
    icon = models.FilePathField(path=f'{utils.get_img_path()}/tenants')

    class Meta:
        db_table = 'tenant'
        ordering = ['id']


class Priority(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)
    icon = models.FilePathField(path=f'{utils.get_img_path()}/priorities')

    class Meta:
        db_table = 'issue_priority'
        ordering = ['id']


class Status(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    type = models.TextChoices('Type', 'ServiceDesk Software')
    description = models.CharField(max_length=255, blank=True)
    color = models.CharField(max_length=7)

    class Meta:
        db_table = 'issue_status'
        ordering = ['id']


class Resolution(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'issue_resolution'
        ordering = ['id']


class Type(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)
    icon = models.FilePathField(path=f'{utils.get_img_path()}/issuetypes')

    class Meta:
        db_table = 'issue_type'
        ordering = ['id']


class Label(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'issue_label'
        ordering = ['id']


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(verbose_name='Created', help_text='Date when issue has been created')
    updated = models.DateTimeField(verbose_name='Updated', blank=True, help_text='Date when issue has been recently changed')

    class Meta:
        db_table = 'issue_comment'
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.now()
            self.author = get_current_user()
        self.updated = datetime.now()
        super().save(*args, **kwargs)


class Issue(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255, help_text='Summarize the issue')
    key = models.CharField(max_length=255)
    description = models.TextField(verbose_name='Description', blank=True, help_text='The content of the issue')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    priority = models.ForeignKey(Priority, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    resolution = models.ForeignKey(Resolution, on_delete=models.CASCADE, blank=True)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE, blank=True)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='%(class)s_related')
    association = models.ManyToManyField('self', through='IssueAssociation', through_fields=('source_issue', 'dest_issue'))
    comments = models.ManyToManyField(Comment, through='CommentAssociation', through_fields=('issue', 'comment'))
    escalated = models.BooleanField(verbose_name='Escalated', default=False)
    suspended = models.BooleanField(verbose_name='Suspended', default=False)
    attachments = models.FileField(upload_to=f'uploads/', blank=True)
    created = models.DateTimeField(verbose_name='Created', help_text='Date when issue has been created')
    updated = models.DateTimeField(verbose_name='Updated', blank=True, help_text='Date when issue has been recently changed')

    class Meta:
        db_table = 'issue'
        # verbose_name = 'issue'
        # verbose_name_plural = 'issues'
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.now()
            self.reporter = get_current_user()
        # if not self.priority:
        #    self.priority = 3
        self.updated = datetime.now()
        if len(self.title) > 200:
            self.title = self.title[:197] + "..."
        super().save(*args, **kwargs)


class IssueAssociation(models.Model):
    source_issue = models.ForeignKey(Issue, on_delete=models.DO_NOTHING, related_name='%(class)s_related')
    dest_issue = models.ForeignKey(Issue, on_delete=models.DO_NOTHING, related_name='%(class)s_related')
    type = models.CharField(max_length=50)

    class Meta:
        db_table = 'issue_association'


class CommentAssociation(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    class Meta:
        db_table = 'comment_association'
