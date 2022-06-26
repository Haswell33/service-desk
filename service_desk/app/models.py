import os.path
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator, FileExtensionValidator, ValidationError
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from django.conf import settings
from django.utils.html import mark_safe, format_html
from django.utils import timezone
from django.db import models
from crum import get_current_user
from tinymce.models import HTMLField
from datetime import datetime
import math

#def TicketAssociation():
#    pass


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png', '.xlsx', '.xls', 'txt']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


def get_upload_path(instance, filename):  # to provide upload path in Attachment
    upload_path = os.path.join(get_media_path(), 'attachments', instance.directory)
    if not os.path.isdir(upload_path):
        os.makedirs(upload_path)
    return os.path.join(upload_path, filename)


def get_media_path():
    return f'{settings.BASE_DIR}/{settings.MEDIA_URL.strip("/")}'


def get_img_field(img, name, height, width):
    return mark_safe(f'<img src="{settings.MEDIA_URL}/{str(img)}" height="{height}" width="{width}" title="{name}" alt={name}/>')


def get_img_text_field(img, name, height, width):
    return mark_safe(f'<div class="img-text_field"><img src="{settings.MEDIA_URL}/{str(img)}" height="{height}" width="{width}" title="{name}" alt={name}/> {name}</div>')


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
        help_text='Number of tickets',
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

    @property
    def icon_img_text(self):
        try:
            return get_img_text_field(self.icon, self.name, 18, 18)
        except AttributeError:
            return self.name
    icon_img_text.fget.short_description = 'Priority'

    def __str__(self):
        return self.name


class Type(models.Model):
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
        upload_to=f'{get_media_path()}/img/type',
        validators=[FileExtensionValidator],
        blank=True,
        max_length=500)

    class Meta:
        db_table = 'type'
        verbose_name = 'type'
        verbose_name_plural = 'types'
        ordering = ['id']

    @property
    def icon_img(self):
        return get_img_field(self.icon, self.name, 20, 20)
    icon_img.fget.short_description = 'Icon'

    @property
    def icon_img_text(self):
        try:
            return get_img_text_field(self.icon, self.name, 18, 18)
        except AttributeError:
            return self.name
    icon_img_text.fget.short_description = 'Type'

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
        blank=True,
        null=True,
        related_name='%(class)s_src_status')
    dest_status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='%(class)s_dest_status')
    types = models.ManyToManyField(
        Type,
        through='TransitionAssociation',
        through_fields=('transition', 'type'))

    class Meta:
        db_table = 'transition'
        verbose_name = 'transition'
        verbose_name_plural = 'transitions'
        ordering = ['src_status']

    @property
    def full_transition(self):
        try:
            src_status = get_status_color(self.src_status.color, self.src_status.name)
        except AttributeError:
            src_status = mark_safe(f'<span style="display: flex; align-items: center">All statuses</span>')
        try:
            dest_status = get_status_color(self.dest_status.color, self.dest_status.name)
        except AttributeError:
            dest_status = mark_safe(f'<span style="display: flex; align-items: center">All statuses</span>')
        return format_html(f'{src_status}<span class="status-arrow"></span>{dest_status}')
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
    content = HTMLField(
        verbose_name='Content')
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
        ordering = ['-created']

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.now()
            self.author = get_current_user()
        if self.id:
            self.updated = datetime.now()
        super().save(*args, **kwargs)

    @property
    def author_img_text(self):
        try:
            return get_img_text_field(self.author.icon, self.author, 18, 18)
        except AttributeError:
            return self.author
    author_img_text.fget.short_description = 'Author'

    def __str__(self):
        return str(self.id)


class Attachment(models.Model):
    id = models.BigAutoField(
        primary_key=True)
    file = models.ImageField(
        upload_to=get_upload_path,
        null=True,
        blank=True,
        max_length=5000)
    filename = models.CharField(
        max_length=255,
        blank=True)
    size = models.IntegerField(
        blank=True,
        editable=False)
    uploaded = models.DateTimeField(
        auto_now_add=True)
    directory = models.CharField(
        max_length=255,
        blank=True)
    user = models.ForeignKey(
        User,
        blank=True,
        on_delete=models.CASCADE,
        related_name='%(class)s_user')

    class Meta:
        db_table = 'attachment'
        verbose_name = 'attachment'
        verbose_name_plural = 'attachments'
        ordering = ['id']

    def save(self, *args, **kwargs):
        self.filename = self.get_filename()
        self.user = get_current_user()
        if not self.size:
            self.size = self.get_size()
        super().save(*args, **kwargs)

    @property
    def uploaded_datetime(self):
        return get_datetime(self.uploaded)
    uploaded_datetime.fget.short_description = 'Uploaded'

    @property
    def display_size(self):
        if self.size == 0:
            return "0B"
        size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(self.size, 1024)))
        p = math.pow(1024, i)
        display_size = round(self.size / p, 2)
        return f'{display_size} {size_names[i]}'
    display_size.fget.short_description = 'Size'

    def get_filename(self):
        return str(self.file).split('/')[-1]

    def get_size(self):
        return self.file.size

    def __str__(self):
        return self.filename


class Ticket(models.Model):
    id = models.BigAutoField(
        primary_key=True)
    key = models.CharField(
        max_length=255,
        unique=True,
        editable=False)
    title = models.CharField(
        max_length=255,
        help_text='Summarize the ticket',
        verbose_name='Title')
    description = HTMLField(
        verbose_name='Description',
        blank=True,
        null=True,
        help_text='Describe the ticket')
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        blank=True,
        related_name='%(class)s_tenant')
    priority = models.ForeignKey(
        Priority,
        on_delete=models.CASCADE,
        default=settings.DEFAULT_PRIORITY_ID,
        related_name='%(class)s_priority',
        verbose_name='Priority')
    status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,
        default=15,
        blank=True,
        related_name='%(class)s_status',
        verbose_name='Status')
    resolution = models.ForeignKey(
        Resolution,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='%(class)s_resolution',
        verbose_name='Resolution')
    type = models.ForeignKey(
        Type,
        on_delete=models.CASCADE,
        default=settings.DEFAULT_ISSUE_TYPE_ID,
        related_name='%(class)s_type',
        verbose_name='Type')
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        related_name='%(class)s_reporter',
        verbose_name='Reporter')
    assignee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='%(class)s_assignee',
        verbose_name='Assignee')
    escalated = models.BooleanField(
        default=False,
        editable=False,
        verbose_name='Escalated')
    suspended = models.BooleanField(
        default=False,
        verbose_name='Suspended')
    created = models.DateTimeField(
        editable=False,
        help_text='Date when ticket has been created',
        verbose_name='Created date')
    updated = models.DateTimeField(
        blank=True,
        null=True,
        editable=False,
        help_text='Date when ticket has been recently changed',
        verbose_name='Updated date')
    slug = models.SlugField(
        max_length=55,
        blank=True)
    relations_out = models.ManyToManyField(
        'self',
        verbose_name='Relations out',
        through='TicketAssociation',
        through_fields=('src_ticket', 'dest_ticket'))
    relations_in = models.ManyToManyField(
        'self',
        verbose_name='Relations out',
        through='TicketAssociation',
        through_fields=('dest_ticket', 'src_ticket'))
    comments = models.ManyToManyField(
        Comment,
        through='CommentAssociation',
        blank=True,
        through_fields=('ticket', 'comment'),
        verbose_name='Comments')
    labels = models.ManyToManyField(
        Label,
        through='LabelAssociation',
        blank=True,
        through_fields=('ticket', 'label'),
        verbose_name='Labels')
    attachments = models.ManyToManyField(
        Attachment,
        through='AttachmentAssociation',
        blank=True,
        through_fields=('ticket', 'attachment'),
        verbose_name='Attachments')

    class Meta:
        db_table = 'ticket'
        verbose_name = 'ticket'
        verbose_name_plural = 'tickets'
        ordering = ['-updated']

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
            self.reporter = get_current_user()
            self.slug = self.key.lower()
        self.updated = timezone.now()
        # send_notifications()
        super(Ticket, self).save(*args, **kwargs)

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
            if self.assignee is None:
                return mark_safe('<div class="ticket-block_info-left">Unassigned</div>')
            else:
                return get_img_text_field(self.assignee.icon, self.assignee, 18, 18)
        except AttributeError:
            return self.assignee
    assignee_img_text.fget.short_description = 'Assignee'

    @property
    def assignee_img(self):
        try:
            if self.assignee is None:
                return mark_safe('<div class="ticket-block_info-left">Unassigned</div>')
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

    '''
    @property
    def get_labels(self):
        return [labels.name for labels in self.labels.all()]

    @property
    def get_attachments(self):
        return [attachments.filename for attachments in self.attachments.all()]
    '''

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Ticket._meta.fields]

    def get_resolution(self):
        if self.resolution is None:
            return mark_safe('<div class="ticket-block_info-left">Unresolved</div>')
        else:
            return self.resolution
    get_resolution.short_description = 'Resolution'

    def getattr(self, field_name):
        return getattr(self, field_name)

    def get_absolute_url(self):
        pass

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


class AuditLog(models.Model):
    id = models.BigAutoField(
        primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_user')
    object = models.PositiveIntegerField()
    object_value = models.CharField(
        max_length=55)
    operation = models.CharField(
        max_length=50,
        blank=True,
        null=True)
    message = models.TextField(
        blank=True,
        null=True)
    content = models.CharField(
        max_length=50,
        blank=True,
        null=True)
    content_value = models.CharField(
        max_length=255,
        blank=True,
        null=True)
    ip_address = models.GenericIPAddressField()
    url = models.URLField()
    session = models.CharField(
        max_length=500)
    created = models.DateTimeField(
        auto_now_add=True)

    class Meta:
        db_table = 'audit_log'
        verbose_name = 'audit log'
        verbose_name_plural = 'audit logs'
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.id:
            # self.created = timezone.now()
            self.user = get_current_user()
        self.message = f'{self.user} {self.ip_address} {self.message}'
        super(AuditLog, self).save(*args, **kwargs)


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

    @property
    def status_color(self):
        return get_status_color(self.status.color, self.status.name)
    status_color.fget.short_description = 'Status'

    def __str__(self):
        return f'{self.board_name}-{self.column}-{self.status}'


class TransitionAssociation(models.Model):
    type = models.ForeignKey(
        Type,
        on_delete=models.CASCADE,
        related_name='%(class)s_type',
        blank=True,
        null=True)
    transition = models.ForeignKey(
        Transition,
        on_delete=models.CASCADE,
        related_name='%(class)s_transition')

    class Meta:
        db_table = 'transition_association'
        verbose_name = 'transition association'
        verbose_name_plural = 'transition associations'
        ordering = ['transition']
        unique_together = ['type', 'transition']

    def __str__(self):
        return f'{self.type} {self.transition}'

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


class TicketAssociation(models.Model):
    src_ticket = models.ForeignKey(
        Ticket,
        on_delete=models.DO_NOTHING,
        related_name='%(class)s_src_ticket')
    dest_ticket = models.ForeignKey(
        Ticket,
        on_delete=models.DO_NOTHING,
        related_name='%(class)s_dest_ticket')

    class Meta:
        db_table = 'ticket_association'
        verbose_name = 'link'
        verbose_name_plural = 'links'

    def __str__(self):
        return f'{self.src_ticket}-{self.dest_ticket}'


class CommentAssociation(models.Model):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='%(class)s_comment')
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='%(class)s_ticket')

    class Meta:
        db_table = 'comment_association'

    def __str__(self):
        return f'{self.ticket}-{self.comment}'


class AttachmentAssociation(models.Model):
    attachment = models.ForeignKey(
        Attachment,
        on_delete=models.CASCADE,
        related_name='%(class)s_attachment')
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='%(class)s_ticket')

    class Meta:
        db_table = 'attachment_association'

    def __str__(self):
        return f'{self.ticket}-{self.attachment}'


class LabelAssociation(models.Model):
    label = models.ForeignKey(
        Label,
        on_delete=models.CASCADE,
        related_name='%(class)s_label')
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='%(class)s_ticket')

    class Meta:
        db_table = 'label_association'

    def __str__(self):
        return f'{self.ticket}-{self.label}'


@receiver(models.signals.post_delete, sender=Attachment)
def auto_delete_file_on_delete(sender, instance, **kwargs):  # Deletes file from filesystem when corresponding `Attachment` object is deleted.
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
