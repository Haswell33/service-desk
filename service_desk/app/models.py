from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator, FileExtensionValidator
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.utils.html import mark_safe, format_html
from django.conf import settings
from django.db import models
from django import forms
from crum import get_current_user
from datetime import datetime
from . import utils

GROUP_TYPES = [
    ('customer', 'Customer'),
    ('operator', 'Operator'),
    ('developer', 'Developer')
]

ENV_TYPES = [
    ('service-desk', 'Service Desk'),
    ('software', 'Software')
]

Group.add_to_class('type', models.CharField(
    max_length=25,
    choices=GROUP_TYPES,
    blank=True,
    db_column='type'))




class Board(models.Model):
    id = models.BigAutoField(
        primary_key=True)
    name = models.CharField(
        max_length=255,
        unique=True)
    env_type = models.CharField(
        max_length=50,
        choices=ENV_TYPES,
        null=True,
        blank=True,)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'board'
        verbose_name = 'board'
        verbose_name_plural = 'boards'


class BoardColumn(models.Model):
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE)
    column_title = models.CharField(
        max_length=255)
    column_number = models.IntegerField(
        default=1
    )

    class Meta:
        db_table = 'board_column'
        verbose_name = 'board column'
        verbose_name_plural = "board columns"
        ordering = ['column_number']

    def __str__(self):
        return f'{self.column_title}'


class SLAScheme(models.Model):
    id = models.BigAutoField(
        primary_key=True)
    name = models.CharField(
        max_length=255,
        unique=True)
    reaction_time = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(43200)],
        help_text='Time to reaction in minutes before escalation')
    resolve_time = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(43200)],
        help_text='Time to resolve in minutes before escalation')
    hour_range = models.CharField(
        max_length=5)

    class Meta:
        db_table = 'sla_scheme'
        verbose_name = 'SLA scheme'
        verbose_name_plural = "SLA schemes"
        ordering = ['id']

    def __str__(self):
        return self.name


class Tenant(models.Model):
    id = models.BigAutoField(
        primary_key=True)
    key = models.CharField(
        max_length=50,
        unique=True)
    name = models.CharField(
        max_length=255)
    count = models.PositiveIntegerField(
        default=0,
        help_text='Number of issues',
        editable=False)
    sla = models.ForeignKey(
        SLAScheme,
        on_delete=models.CASCADE)
    customers_group = models.ForeignKey(
        Group,
        related_name='%(class)s_customers_group',
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING)
    operators_group = models.ForeignKey(
        Group,
        related_name='%(class)s_operators_group',
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING)
    developers_group = models.ForeignKey(
        Group,
        related_name='%(class)s_developers_group',
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING)
    customers_board = models.ForeignKey(
        Board,
        related_name='%(class)s_customers_board',
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING)
    operators_board = models.ForeignKey(
        Board,
        related_name='%(class)s_operators_board',
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING)
    developers_board = models.ForeignKey(
        Board,
        related_name='%(class)s_developers_board',
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING)
    icon = models.ImageField(
        upload_to=f'{(settings.STATIC_URL).strip("/")}/images/tenant',
        validators=[FileExtensionValidator],
        blank=True,
        max_length=500)

    class Meta:
        db_table = 'tenant'
        verbose_name = 'tenant'
        verbose_name_plural = 'tenants'
        ordering = ['id']
        permissions = [
            ('view_customer_space', 'Manage tenant as customer'),
            ('view_operator_space', 'Manage tenant as operator'),
            ('view_developer_space', 'Manage tenant as developer')
        ]

    def save(self, *args, **kwargs):
        if not self.id:
            self.count = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def icon_img_admin(self):
        return mark_safe(f'<img src="../../../{self.icon}" height="20" width="20"/>')

    def icon_img(self):
        return mark_safe(f'<img src="{self.icon}" height="20" width="20"/>')

    icon_img_admin.short_description = 'Icon'
    icon_img.short_description = 'Icon'


class Priority(models.Model):
    id = models.BigAutoField(
        primary_key=True)
    name = models.CharField(
        max_length=50,
        unique=True)
    description = models.TextField(
        name='description',
        blank=True,
        null=True)
    icon = models.ImageField(
        upload_to=f'{(settings.STATIC_URL).strip("/")}/images/priority',
        validators=[FileExtensionValidator],
        blank=True,
        max_length=500)

    class Meta:
        db_table = 'priority'
        verbose_name = 'priority'
        verbose_name_plural = 'priorities'
        ordering = ['id']

    def __str__(self):
        return self.name

    def icon_img_admin(self):
        return mark_safe(f'<img src="../../../{self.icon}" height="20" width="20"/>')

    def icon_img(self):
        return mark_safe(f'<img src="{self.icon}" height="20" width="20"/>')

    icon_img_admin.short_description = 'Icon'
    icon_img.short_description = 'Icon'


class IssueType(models.Model):
    id = models.BigAutoField(
        primary_key=True)
    name = models.CharField(
        max_length=50,
        unique=True)
    env_types = models.CharField(
        max_length=50,
        choices=ENV_TYPES,
        name='env_type',
        null=True)
    description = models.TextField(
        name='description',
        blank=True,
        null=True)
    icon = models.ImageField(
        upload_to=f'{(settings.STATIC_URL).strip("/")}/images/issue_type',
        validators=[FileExtensionValidator],
        blank=True,
        max_length=500)

    class Meta:
        db_table = 'issue_type'
        verbose_name = 'issue type'
        verbose_name_plural = 'issue types'
        ordering = ['id']

    def __str__(self):
        return self.name

    def icon_img_admin(self):
        return mark_safe(f'<img src="../../../{self.icon}" height="20" width="20"/>')

    def icon_img(self):
        return mark_safe(f'<img src="{self.icon}" height="20" width="20"/>')

    icon_img_admin.short_description = 'Icon'
    icon_img.short_description = 'Icon'


class Resolution(models.Model):
    id = models.BigAutoField(
        primary_key=True)
    name = models.CharField(
        max_length=50,
        unique=True)
    description = models.TextField(
        name='description',
        blank=True,
        null=True)

    class Meta:
        db_table = 'resolution'
        verbose_name = 'resolution'
        verbose_name_plural = 'resolutions'
        ordering = ['id']

    def __str__(self):
        return self.name


class Status(models.Model):
    id = models.BigAutoField(
        primary_key=True)
    name = models.CharField(
        max_length=50,
        unique=True)
    step = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
        default=1,
        help_text='Order of status')
    board_column = models.ManyToManyField(
        BoardColumn,
        through='BoardColumnAssociation',
        through_fields=('status', 'column'))
    description = models.TextField(
        name='description',
        blank=True,
        null=True)
    resolution = models.ForeignKey(
        Resolution,
        on_delete=models.CASCADE,
        related_name='%(class)s_resolution',
        blank=True,
        null=True)
    color = models.CharField(
        max_length=7,
        help_text='RGB color in HEX format')
    transitions = models.ManyToManyField(
        'self',
        through='Transition',
        through_fields=('src_status', 'dest_status'))

    class Meta:
        db_table = 'status'
        verbose_name = 'status'
        verbose_name_plural = 'statuses'
        ordering = ['name']

    def color_hex(self):
        return format_html(f'<div style="background: {self.color};width: 20px; height: 20px; border-radius: 4px;"></div>')

    def get_step(self):
        return self.step

    def __str__(self):
        return self.name

    color_hex.short_description = 'Color'


class Transition(models.Model):
    name = models.CharField(max_length=55)
    src_status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,
        related_name='%(class)s_src_status')
    dest_status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,
        related_name='%(class)s_dest_status')

    class Meta:
        db_table = 'transition'
        verbose_name = 'transition'
        verbose_name_plural = 'transitions'
        ordering = ['src_status']

    def __str__(self):
        return f'{self.src_status} -> {self.dest_status}'

    def full_transition(self):
        src_status_color = Status.objects.filter(name=self.src_status).values_list('color')[0][0]
        dest_status_color = Status.objects.filter(name=self.dest_status).values_list('color')[0][0]
        return format_html(
            f'<div style="background-color: {src_status_color};" class="admin-transition">{self.src_status}</div>'
            f'<span class="admin-transition-arrow"></span>'
            f'<div style="background-color: {dest_status_color};" class="admin-transition">{self.dest_status}</div>')
        # return f'{self.src_status} -> {self.dest_status}'

    full_transition.short_description = 'Transition'


class Label(models.Model):
    id = models.BigAutoField(
        primary_key=True)
    name = models.CharField(
        max_length=255,
        unique=True)
    description = models.TextField(
        name='description',
        blank=True,
        null=True)

    class Meta:
        db_table = 'label'
        verbose_name = 'label'
        verbose_name_plural = 'labels'
        ordering = ['id']

    def __str__(self):
        return self.name


class Comment(models.Model):
    id = models.BigAutoField(
        primary_key=True)
    content = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        blank=True,
        related_name='%(class)s_author')
    created = models.DateTimeField(
        verbose_name='Created',
        blank=True,
        help_text='Date when comment has been created')
    updated = models.DateTimeField(
        verbose_name='Updated',
        blank=True,
        null=True,
        help_text='Date when comment has been recently changed')

    class Meta:
        db_table = 'comment'
        verbose_name = 'comment'
        verbose_name_plural = 'comments'
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.now()
            self.author = get_current_user()
        self.updated = datetime.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.id


class Attachment(models.Model):
    id = models.BigAutoField(
        primary_key=True)
    file = models.FileField(
        upload_to=f'{(settings.STATIC_URL).strip("/")}/attachments',
        validators=[FileExtensionValidator],
        blank=True)
    filename = models.CharField(
        max_length=255,
        blank=True)
    size = models.IntegerField(
        blank=True)

    class Meta:
        db_table = 'attachment'
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

    def __str__(self):
        return self.id


class Issue(models.Model):
    id = models.BigAutoField(
        primary_key=True)
    key = models.CharField(
        max_length=255,
        editable=False)
    title = models.CharField(
        max_length=255,
        help_text='Summarize the issue')
    description = models.TextField(
        verbose_name='Description',
        blank=True,
        null=True,
        help_text='The content of the issue')
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        blank=True,
        related_name='%(class)s_tenant')
    priority = models.ForeignKey(
        Priority,
        on_delete=models.CASCADE,
        related_name='%(class)s_priority')
    status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,
        related_name='%(class)s_status')
    resolution = models.ForeignKey(
        Resolution,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='%(class)s_resolution')
    type = models.ForeignKey(
        IssueType,
        on_delete=models.CASCADE,
        related_name='%(class)s_type')
    label = models.ForeignKey(
        Label,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='%(class)s_label')
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        related_name='%(class)s_reporter')
    assignee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='%(class)s_assignee')
    escalated = models.BooleanField(
        default=False, editable=False)
    suspended = models.BooleanField(
        default=False, editable=False)
    created = models.DateTimeField(
        editable=False,
        help_text='Date when issue has been created')
    updated = models.DateTimeField(
        blank=True,
        null=True,
        editable=False,
        help_text='Date when issue has been recently changed')
    associations = models.ManyToManyField(
        'self',
        through='IssueAssociation',
        through_fields=('src_issue', 'dest_issue'))
    comments = models.ManyToManyField(
        Comment,
        through='CommentAssociation',
        through_fields=('issue', 'comment'))
    attachments = models.ManyToManyField(
        Attachment,
        blank=True,
        through='AttachmentAssociation',
        through_fields=('issue', 'attachment'))

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

    def __str__(self):
        return self.key


class BoardColumnAssociation(models.Model):
    column = models.ForeignKey(
        BoardColumn,
        on_delete=models.CASCADE,
        related_name='%(class)s_column_nr')
    status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,
        related_name='%(class)s_status')

    class Meta:
        db_table = 'board_column_association'
        verbose_name = 'board column association'
        verbose_name_plural = 'board column associations'
        ordering = ['column']

    def board(self):
        return BoardColumn.objects.filter(column_title=self.column).values_list('board')[0]

    def __str__(self):
        return f'{self.board()}-{self.column}-{self.status}'

    board.short_description = 'Board'


class TransitionAssociation(models.Model):
    issue_type = models.ForeignKey(
        IssueType,
        on_delete=models.CASCADE,
        related_name='%(class)s_issue_type')
    transition = models.ForeignKey(
        Transition,
        on_delete=models.CASCADE,
        related_name='%(class)s_transition')

    class Meta:
        db_table = 'transition_association'
        verbose_name = 'transition association'
        verbose_name_plural = 'transition associations'
        ordering = ['transition']
        unique_together = ['issue_type', 'transition']

    def __str__(self):
        return f'{self.issue_type} {self.transition}'

    def full_transition(self):
        src_status = str(self.transition).split(' -> ')[0]
        dest_status = str(self.transition).split(' -> ')[1]
        src_status_color = Status.objects.filter(name=src_status).values_list('color')[0][0]
        dest_status_color = Status.objects.filter(name=dest_status).values_list('color')[0][0]
        return format_html(
            f'<div style="background-color: {src_status_color};" class="admin-transition">{src_status}</div>'
            f'<span class="admin-transition-arrow"></span>'
            f'<div style="background-color: {dest_status_color};" class="admin-transition">{dest_status}</div>')
        # return f'{self.src_status} -> {self.dest_status}'

    full_transition.short_description = 'Transition'


class IssueAssociation(models.Model):
    src_issue = models.ForeignKey(
        Issue,
        on_delete=models.DO_NOTHING,
        related_name='%(class)s_src_issue')
    dest_issue = models.ForeignKey(
        Issue,
        on_delete=models.DO_NOTHING,
        related_name='%(class)s_dest_issue')

    class Meta:
        db_table = 'issue_association'
        verbose_name = 'link'
        verbose_name_plural = 'links'

    def __str__(self):
        return f'{self.src_issue}-{self.dest_issue}'


class CommentAssociation(models.Model):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='%(class)s_comment')
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name='%(class)s_issue')

    class Meta:
        db_table = 'comment_association'

    def __str__(self):
        return f'{self.issue}-{self.comment}'


class AttachmentAssociation(models.Model):
    attachment = models.ForeignKey(
        Attachment,
        on_delete=models.CASCADE,
        related_name='%(class)s_attachment')
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name='%(class)s_issue')

    class Meta:
        db_table = 'attachment_association'

    def __str__(self):
        return f'{self.issue}-{self.attachment}'


# FORMS


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'type', 'priority', 'assignee', 'label', 'description', 'attachments']
