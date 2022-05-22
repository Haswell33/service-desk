import os
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator, FileExtensionValidator
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.conf import settings
from crum import get_current_user
from django.utils.html import format_html
from datetime import datetime
from . import utils


GROUP_TYPES = [
    ('customer', 'Customer'),
    ('operator', 'Operator'),
    ('developer', 'Developer')
]

TYPES = [
    ('SD', 'Service Desk'),
    ('software', 'Software')
]

STATUS_COLOR_TYPES = [
    ('SD', 'Beginning'),
    ('Software', 'Progress'),
    ('', 'Finalization')
]

Group.add_to_class('type', models.CharField(max_length=25, choices=GROUP_TYPES, blank=True, db_column='type'))


class SLA(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    reaction_time = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(43200)], help_text='Time to reaction in minutes before escalation')
    resolve_time = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(43200)], help_text='Time to resolve in minutes before escalation')
    hour_range = models.CharField(max_length=5)

    class Meta:
        db_table = 'tenant_sla'
        verbose_name = 'SLA'
        verbose_name_plural = "SLA's"
        ordering = ['id']


class Workflow(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    pattern = models.TextField(help_text='XML file to descript workflow')

    class Meta:
        db_table = 'tenant_workflow'
        verbose_name = 'workflow'
        verbose_name_plural = 'workflows'


class Tenant(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=50, unique=True, blank=True)
    count = models.PositiveIntegerField(blank=True, default=0)
    sla = models.ForeignKey(SLA, on_delete=models.CASCADE)
    workflow_operator = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='%(class)s_workflow_operator', help_text='Workflow scheme for Service Desk space')
    workflow_developer = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='%(class)s_workflow_developer', help_text='Workflow scheme for Developer space')
    customers_group = models.ForeignKey(Group, related_name='%(class)s_customers_group', blank=True, null=True, on_delete=models.DO_NOTHING)
    operators_group = models.ForeignKey(Group, related_name='%(class)s_operators_group', blank=True, null=True, on_delete=models.DO_NOTHING)
    developers_group = models.ForeignKey(Group, related_name='%(class)s_developers_group', blank=True, null=True, on_delete=models.DO_NOTHING)
    icon = models.FilePathField(path=f'{utils.get_img_path()}/tenants/')

    class Meta:
        db_table = 'tenant'
        verbose_name = 'tenant'
        verbose_name_plural = 'tenants'
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.id:
            self.count = 0


class Priority(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(verbose_name='Description', blank=True, null=True)
    icon = models.FilePathField(path=f'{utils.get_img_path()}/priorities')

    class Meta:
        db_table = 'issue_priority'
        verbose_name = 'priority'
        verbose_name_plural = 'priorities'
        ordering = ['id']


class Status(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=50, choices=TYPES, name='status_type', null=True, verbose_name='Type')
    description = models.TextField(verbose_name='Description', blank=True, null=True)
    color = models.CharField(max_length=7)

    class Meta:
        db_table = 'issue_status'
        verbose_name = 'status'
        verbose_name_plural = 'statuses'


class Resolution(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(verbose_name='Description', blank=True, null=True)

    class Meta:
        db_table = 'issue_resolution'
        verbose_name = 'resolution'
        verbose_name_plural = 'resolutions'
        ordering = ['id']


class Type(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=50, choices=TYPES, name='Type', null=True)
    description = models.TextField(verbose_name='Description', blank=True, null=True)
    icon = models.FilePathField(path=f'{utils.get_img_path()}/issuetypes')

    class Meta:
        db_table = 'issue_type'
        verbose_name = 'issue type'
        verbose_name_plural = 'issue types'
        ordering = ['id']


class Label(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(verbose_name='Description', blank=True, null=True)

    class Meta:
        db_table = 'issue_label'
        verbose_name = 'label'
        verbose_name_plural = 'labels'
        ordering = ['id']


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, related_name='%(class)s_author')
    created = models.DateTimeField(verbose_name='Created', blank=True, help_text='Date when issue has been created')
    updated = models.DateTimeField(verbose_name='Updated', blank=True, null=True, help_text='Date when issue has been recently changed')

    class Meta:
        db_table = 'issue_comment'
        verbose_name = 'comment'
        verbose_name_plural = 'comments'
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.now()
            self.author = get_current_user()
        self.updated = datetime.now()
        super().save(*args, **kwargs)


class Attachment(models.Model):
    id = models.BigAutoField(primary_key=True)
    file = models.FileField(upload_to=f'uploads/attachments/', blank=True, validators=[FileExtensionValidator])
    filename = models.CharField(max_length=255, blank=True)
    size = models.IntegerField(blank=True)

    class Meta:
        db_table = 'issue_attachment'
        verbose_name = 'attachment'
        verbose_name_plural = 'attachments'
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.size:
            self.size = self.get_size()
        if not self.filename:
            self.filename = self.get_filename()
        super().save(*args, **kwargs)

    def get_filename(self):
        return str(self.file)

    def get_size(self):
        return self.file.__sizeof__()


class Issue(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255, help_text='Summarize the issue')
    key = models.CharField(max_length=255, unique=True, blank=True)
    description = models.TextField(verbose_name='Description', blank=True, null=True, help_text='The content of the issue')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, blank=True, related_name='%(class)s_tenant')
    priority = models.ForeignKey(Priority, on_delete=models.CASCADE, related_name='%(class)s_priority')
    status = models.ForeignKey(Status, on_delete=models.CASCADE, related_name='%(class)s_status')
    resolution = models.ForeignKey(Resolution, on_delete=models.CASCADE, blank=True, null=True, related_name='%(class)s_resolution')
    type = models.ForeignKey(Type, on_delete=models.CASCADE, related_name='%(class)s_type')
    label = models.ForeignKey(Label, on_delete=models.CASCADE, blank=True, null=True, related_name='%(class)s_label')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='%(class)s_reporter')
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='%(class)s_assignee')
    attachments = models.ForeignKey(Attachment, on_delete=models.CASCADE, blank=True, null=True, related_name='%(class)s_attachment')
    association = models.ManyToManyField('self', through='IssueAssociation', through_fields=('src_issue', 'dest_issue'))
    comments = models.ManyToManyField(Comment, through='CommentAssociation', through_fields=('issue', 'comment'))
    escalated = models.BooleanField(default=False)
    suspended = models.BooleanField(default=False)
    created = models.DateTimeField(help_text='Date when issue has been created')
    updated = models.DateTimeField(blank=True, null=True, help_text='Date when issue has been recently changed')

    class Meta:
        db_table = 'issue'
        verbose_name = 'issue'
        verbose_name_plural = 'issues'
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.now()
            self.reporter = get_current_user()
            self.key = f'{Tenant.key}-{Tenant.count}'
            Tenant.count = Tenant.count + 1
            Tenant.save(Tenant())
        self.updated = datetime.now()
        # send_notifications()
        if len(self.title) > 200:
            self.title = f'{self.title[:180]}...'
        super(Issue, self).save(*args, **kwargs)

    def _escalate(self):
        self.escalated = True
        self.save()

    def _suspend(self):
        self.suspended = True
        self.save()

    @property
    def is_escalated(self):
        return self.escalated

    @property
    def is_suspended(self):
        return self.suspended

    @property
    def is_resolved(self):
        if self.resolution:
            return True
        else:
            return False


class IssueAssociation(models.Model):
    src_issue = models.ForeignKey(Issue, on_delete=models.DO_NOTHING, related_name='%(class)s_src_issue')
    dest_issue = models.ForeignKey(Issue, on_delete=models.DO_NOTHING, related_name='%(class)s_dest_issue')
    type = models.CharField(max_length=50)

    class Meta:
        db_table = 'issue_association'
        verbose_name = 'link'
        verbose_name_plural = 'links'
        ordering = ['id']


class CommentAssociation(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='%(class)s_comment')
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='%(class)s_issue')

    class Meta:
        db_table = 'comment_association'
