from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator, FileExtensionValidator
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.utils.html import mark_safe, format_html
from django.utils import timezone
from django.db import models
from crum import get_current_user
from tinymce.models import HTMLField
from datetime import datetime


def get_media_path():
    return f'{settings.BASE_DIR}/{settings.MEDIA_URL.strip("/")}'


def get_img_field(img, name, height, width):
    return mark_safe(f'<img src="{settings.MEDIA_URL}/{str(img)}" height="{height}" width="{width}" title="{name}" alt={name}/>')


def get_img_text_field(img, name, height, width):
    return mark_safe(f'<img src="{settings.MEDIA_URL}/{str(img)}" height="{height}" width="{width}" title="{name}" alt={name}/> {name}')


def get_status_color(color, name):
    return mark_safe(f'<div style="background-color: {color};" class="status" title="{name}">{name}</div>')


def get_datetime(date):
    return datetime.strftime(date, '%Y/%m/%d %H:%M:%S')


Group.add_to_class(
    'type', models.CharField(
        max_length=25,
        choices=settings.GROUP_TYPES,
        blank=True,
        db_column='type'))

User.add_to_class(
    'icon', models.ImageField(
        upload_to=f'{get_media_path()}/img/user',
        validators=[FileExtensionValidator],
        default=f'img/user/default-avatar.png',
        max_length=500))


class Board(models.Model):
    id = models.BigAutoField(
        primary_key=True)
    name = models.CharField(
        max_length=255,
        unique=True)
    env_type = models.CharField(
        max_length=50,
        choices=settings.ENV_TYPES,
        verbose_name='Environment type',
        null=True,
        blank=True)

    class Meta:
        db_table = 'board'
        verbose_name = 'board'
        verbose_name_plural = 'boards'

    def __str__(self):
        return self.name


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
        upload_to=f'{get_media_path()}/img/tenant',
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

    @property
    def icon_img(self):
        return get_img_field(self.icon, self.name, 20, 20)
    icon_img.fget.short_description = 'Icon'

    def __str__(self):
        return self.name


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
    step = models.IntegerField(
        default=1)
    icon = models.ImageField(
        upload_to=f'{get_media_path()}/img/priority',
        validators=[FileExtensionValidator],
        blank=True,
        max_length=500)

    class Meta:
        db_table = 'priority'
        verbose_name = 'priority'
        verbose_name_plural = 'priorities'
        ordering = ['-step']

    @property
    def icon_img(self):
        return get_img_field(self.icon, self.name, 20, 20)
    icon_img.fget.short_description = 'Icon'

    def __str__(self):
        return self.name


class IssueType(models.Model):
    id = models.BigAutoField(
        primary_key=True)
    name = models.CharField(
        max_length=50,
        unique=True)
    env_types = models.CharField(
        max_length=50,
        choices=settings.ENV_TYPES,
        name='env_type',
        verbose_name='Environment type',
        null=True)
    description = models.TextField(
        name='description',
        blank=True,
        null=True)
    icon = models.ImageField(
        upload_to=f'{get_media_path()}/img/issue_type',
        validators=[FileExtensionValidator],
        blank=True,
        max_length=500)

    class Meta:
        db_table = 'issue_type'
        verbose_name = 'issue type'
        verbose_name_plural = 'issue types'
        ordering = ['id']

    @property
    def icon_img(self):
        return get_img_field(self.icon, self.name, 20, 20)
    icon_img.fget.short_description = 'Icon'

    def __str__(self):
        return self.name


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
    #board_column = models.ManyToManyField(
    #    BoardColumn,
    #    through='BoardColumnAssociation',
    #    through_fields=('status', 'column'))
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

    @property
    def color_hex(self):
        return format_html(f'<div style="background: {self.color}; width: 20px; height: 20px; border-radius: 4px;"></div>')
    color_hex.fget.short_description = 'Color'

    @property
    def status_color(self):
        return get_status_color(self.color, self.name)
    status_color.fget.short_description = 'Status'

    def __str__(self):
        return self.name


class BoardColumn(models.Model):
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE)
    column_title = models.CharField(
        max_length=255)
    column_number = models.IntegerField(
        default=1)
    statuses = models.ManyToManyField(
        Status,
        through='BoardColumnAssociation',
        through_fields=('column', 'status'))

    class Meta:
        db_table = 'board_column'
        verbose_name = 'board column'
        verbose_name_plural = "board columns"
        ordering = ['column_number']

    def __str__(self):
        return self.column_title


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

    @property
    def full_transition(self):
        return format_html(
            f'{get_status_color(self.src_status.color, self.src_status.name)}'
            f'<span class="status-arrow"></span>'
            f'{get_status_color(self.dest_status.color, self.dest_status.name)}')
    full_transition.fget.short_description = 'Transition'

    def __str__(self):
        return f'{self.src_status} -> {self.dest_status}'


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
        help_text='Date when comment created')
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
        timezone.now()
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
        upload_to=f'{get_media_path()}/attachments',
        validators=[FileExtensionValidator],
        blank=True,
        null=True)
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
        unique=True,
        editable=False)
    title = models.CharField(
        max_length=255,
        help_text='Summarize the issue')
    description = HTMLField(
        verbose_name='description',
        blank=True,
        null=True,
        help_text='Describe the issue')
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        blank=True,
        related_name='%(class)s_tenant')
    priority = models.ForeignKey(
        Priority,
        on_delete=models.CASCADE,
        default=settings.DEFAULT_PRIORITY_ID,
        related_name='%(class)s_priority')
    status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,
        default=15,
        blank=True,
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
        default=settings.DEFAULT_ISSUE_TYPE_ID,
        related_name='%(class)s_type')
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
        default=False,
        editable=False)
    suspended = models.BooleanField(
        default=False)
    created = models.DateTimeField(
        editable=False,
        help_text='Date when issue has been created')
    updated = models.DateTimeField(
        blank=True,
        null=True,
        editable=False,
        help_text='Date when issue has been recently changed')
    slug = models.SlugField(
        max_length=55,
        blank=True)
    associations = models.ManyToManyField(
        'self',
        through='IssueAssociation',
        through_fields=('src_issue', 'dest_issue'))
    comments = models.ManyToManyField(
        Comment,
        through='CommentAssociation',
        blank=True,
        through_fields=('issue', 'comment'))
    labels = models.ManyToManyField(
        Label,
        through='LabelAssociation',
        blank=True,
        through_fields=('issue', 'label'))
    attachments = models.ManyToManyField(
        Attachment,
        through='AttachmentAssociation',
        blank=True,
        through_fields=('issue', 'attachment'))

    class Meta:
        db_table = 'issue'
        verbose_name = 'issue'
        verbose_name_plural = 'issues'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
            self.reporter = get_current_user()
            self.slug = self.key.lower()
        self.updated = timezone.now()
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

    @property
    def type_img(self):
        return get_img_field(self.type.icon, self.type.name, 18, 18)
    type_img.fget.short_description = 'Type'

    @property
    def priority_img(self):
        return get_img_field(self.priority.icon, self.priority.name, 18, 18)
    priority_img.fget.short_description = 'Priority'

    @property
    def assignee_img_text(self):
        try:
            return get_img_text_field(self.assignee.icon, self.assignee, 18, 18)
        except AttributeError:
            return self.assignee
    assignee_img_text.fget.short_description = 'Assignee'

    @property
    def assignee_img(self):
        try:
            if self.assignee is None:
                return mark_safe('<div class="ticket-block_info">Unassigned</div>')
            else:
                return get_img_field(self.assignee.icon, self.assignee, 20, 20)
        except AttributeError:
            return self.assignee

    assignee_img.fget.short_description = 'Assignee'

    @property
    def reporter_img_text(self):
        try:
            return get_img_text_field(self.reporter.icon, self.reporter, 18, 18)
        except AttributeError:
            return self.reporter
    reporter_img_text.fget.short_description = 'Reporter'

    @property
    def reporter_img(self):
        try:
            return get_img_field(self.reporter.icon, self.reporter, 20, 20)
        except AttributeError:
            return self.reporter
    reporter_img.fget.short_description = 'Reporter'

    @property
    def status_color(self):
        return get_status_color(self.status.color, self.status.name)
    status_color.fget.short_description = 'Status'

    @property
    def created_datetime(self):
        return get_datetime(self.created)
    created_datetime.fget.short_description = 'Created'

    @property
    def updated_datetime(self):
        return get_datetime(self.updated)
    updated_datetime.fget.short_description = 'Updated'

    @property
    def get_labels(self):
        return "\n".join([p.labels for p in self.label.all()])

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Issue._meta.fields]

    def __str__(self):
        return self.key


class TenantSession(models.Model):
    id = models.BigAutoField(
        primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_user')
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='%(class)s_tenant')
    active = models.BooleanField(
        default=False,
        editable=False)
    user_type = models.CharField(
        max_length=25,
        choices=settings.GROUP_TYPES)

    class Meta:
        db_table = 'tenant_session'
        verbose_name = 'tenant session'
        verbose_name_plural = 'tenant sessions'
        ordering = ['id']

    def __str__(self):
        return f'{self.tenant.key}-{self.user.username}-{self.user_type}'


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

    @property
    def board_name(self):
        return self.column.board
    board_name.fget.short_description = 'Board'

    #@property
    #def column_on_board(self):
    #    return f'{self.column}-{self.column.board}'
    #column_on_board.fget.short_description = 'Column'

    @property
    def status_color(self):
        return get_status_color(self.status.color, self.status.name)
    status_color.fget.short_description = 'Status'

    def __str__(self):
        return f'{self.board_name}-{self.column}-{self.status}'


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

    @property
    def full_transition(self):
        src_status_name = str(self.transition).split(' -> ')[0]
        dest_status_name = str(self.transition).split(' -> ')[1]
        src_status = Status.objects.get(name=src_status_name)
        dest_status = Status.objects.get(name=dest_status_name)
        return format_html(
            f'{get_status_color(src_status.color, src_status.name)}'
            f'<span class="status-arrow"></span>'
            f'{get_status_color(dest_status.color, dest_status.name)}')
    full_transition.fget.short_description = 'Transition'


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


class LabelAssociation(models.Model):
    label = models.ForeignKey(
        Label,
        on_delete=models.CASCADE,
        related_name='%(class)s_label')
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name='%(class)s_issue')

    class Meta:
        db_table = 'label_association'

    def __str__(self):
        return f'{self.issue}-{self.label}'
