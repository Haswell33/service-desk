from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator, ValidationError
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib.auth.models import Group, AbstractBaseUser, PermissionsMixin
from django.db.models import Q, Manager
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from crum import get_current_user, get_current_request
from tinymce.models import HTMLField
from datetime import datetime
from .utils import ticket_manager, utils
from .managers import UserManager
from logging import getLogger
import os

logger = getLogger(__name__)


def get_upload_path(instance, filename):  # to provide upload path in Attachment
    upload_path = os.path.join(utils.get_media_path(), 'attachments', instance.directory)
    if not os.path.isdir(upload_path):
        os.makedirs(upload_path)
    return os.path.join(upload_path, filename)


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = settings.ALLOW_FILE_EXTENSIONS
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


Group.add_to_class(
    'role', models.CharField(
        max_length=25,
        choices=settings.ROLES,
        blank=True,
        db_column='role'))


class User(AbstractBaseUser):
    username = models.CharField(
        max_length=25,
        unique=True)
    first_name = models.CharField(
        max_length=15)
    last_name = models.CharField(
        max_length=15)
    email = models.EmailField(
        _('email address'))
    icon = models.ImageField(
        upload_to=f'{utils.get_media_path()}/img/user',
        default=f'img/user/dog.png',
        max_length=500)
    password = models.CharField(
        max_length=500)
    manager = models.BooleanField(
        default=False)
    admin = models.BooleanField(
        default=False)
    active = models.BooleanField(
        default=True)
    created = models.DateTimeField(
        default=timezone.now)
    last_login = models.DateTimeField(
        blank=True,
        null=True)
    groups = models.ManyToManyField(
        related_query_name='user',
        related_name='user_set',
        to='auth.Group',
        blank=True)
    permissions = models.ManyToManyField(
        related_query_name='user',
        related_name='user_set',
        to='auth.Permission',
        blank=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'admin', 'manager']

    objects = UserManager()

    class Meta:
        db_table = 'user'
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_display_name(self):
        return f'{str(self.first_name).capitalize()} {str(self.last_name).capitalize()}'

    def get_icon(self):
        return utils.get_img_field(self.icon, self.get_display_name(), 20, 20)
    get_icon.short_description = 'Icon'

    def get_icon_text(self):
        try:
            return utils.get_img_text_field(self.icon, self, 18, 18)
        except AttributeError:
            return self
    get_icon_text.short_description = 'User'

    @property
    def is_staff(self):
        return self.manager

    @property
    def is_superuser(self):
        return self.admin

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_customer(self):
        if TenantSession.get_active(self).role == settings.CUST_TYPE:
            return True
        else:
            return False

    @property
    def is_operator(self):
        if TenantSession.get_active(self).role == settings.OPER_TYPE:
            return True
        else:
            return False

    @property
    def is_developer(self):
        if TenantSession.get_active(self).role == settings.DEV_TYPE:
            return True
        else:
            return False

    def has_perm(self, perm, obj=None):
        return self.admin

    def has_module_perms(self, app_label):
        return self.admin

    def __str__(self):
        if self.first_name and self.last_name:
            return self.get_display_name()
        else:
            return self.username


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

    objects = Manager()

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

    objects = models.Manager()

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
        upload_to=f'{utils.get_media_path()}/img/tenant',
        validators=[FileExtensionValidator],
        blank=True,
        max_length=500)

    objects = Manager()

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

    def get_icon(self):
        return utils.get_img_field(self.icon, self.name, 20, 20)
    get_icon.short_description = 'Icon'

    def session_exists(self, user):  # check if specific tenant session assigned to provided user exists in database
        if TenantSession.objects.filter(tenant=self, user=user):
            return True
        else:
            return False

    @staticmethod
    def get_active(user):
        active_tenant_session = TenantSession.get_active(user)
        return Tenant.objects.get(id=active_tenant_session.tenant.id)

    def add_session(self, role, user):  # creates tenant session record in database for selected user
        TenantSession.objects.create(tenant=self, role=role, user=user)

    def set_active_session(self, request):  # change tenant state to active based on data in cookies or choose default if no data in cookies
        def _set_active_tenant(instance, user):
            tenant_session = TenantSession.objects.get(tenant=instance, user=user)
            tenant_session.active = True
            tenant_session.save()
        tenant_cookie = self.get_cookie_name(request.user)
        if request.COOKIES.get(tenant_cookie) is None and not TenantSession.objects.filter(active=True, user=request.user):
            _set_active_tenant(self, request.user)
        elif request.COOKIES.get(tenant_cookie) == str(self.id):
            _set_active_tenant(self, request.user)

    @staticmethod
    def get_cookie_name(user):
        return f'active_tenant_id_{str(user.id)}'

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
        upload_to=f'{utils.get_media_path()}/img/priority',
        validators=[FileExtensionValidator],
        blank=True,
        max_length=500)

    objects = models.Manager()

    class Meta:
        db_table = 'priority'
        verbose_name = 'priority'
        verbose_name_plural = 'priorities'
        ordering = ['-step']

    def get_icon(self):
        return utils.get_img_field(self.icon, self.name, 20, 20)
    get_icon.short_description = 'Icon'

    def get_icon_text(self):
        try:
            return utils.get_img_text_field(self.icon, self.name, 18, 18)
        except AttributeError:
            return self.name
    get_icon_text.short_description = 'Priority'

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
        upload_to=f'{utils.get_media_path()}/img/type',
        validators=[FileExtensionValidator],
        blank=True,
        max_length=500)

    objects = models.Manager()

    class Meta:
        db_table = 'type'
        verbose_name = 'type'
        verbose_name_plural = 'types'
        ordering = ['id']

    def get_icon(self):
        return utils.get_img_field(self.icon, self.name, 20, 20)
    get_icon.short_description = 'Icon'

    def get_icon_text(self):
        try:
            return utils.get_img_text_field(self.icon, self.name, 18, 18)
        except AttributeError:
            return self.name
    get_icon_text.short_description = 'Type'

    @staticmethod
    def get_options(user):
        if user.is_operator or user.is_admin:
            return Type.objects.all()
        elif user.is_customer:
            return Type.objects.filter(env_type=settings.SD_ENV_TYPE)
        elif user.is_developer:
            return Type.objects.filter(env_type=settings.SOFT_ENV_TYPE)

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

    objects = models.Manager()

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

    objects = models.Manager()

    class Meta:
        db_table = 'status'
        verbose_name = 'status'
        verbose_name_plural = 'statuses'
        ordering = ['name']

    @property
    def color_hex(self):
        return utils.get_color_box(self.color, '18', '18')
    color_hex.fget.short_description = 'Color'

    def get_colored(self):
        return utils.get_status_color(self.color, self.name)
    get_colored.short_description = 'Status'

    @staticmethod
    def get_available_status_list(user):
        active_tenant_tickets = TenantSession.get_active(user).get_tickets(user)
        available_statuses = []
        for status in active_tenant_tickets.order_by('status__name').distinct('status__name').values_list('status'):
            available_statuses.append(str(status[0]))
        return Status.objects.filter(id__in=available_statuses)

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

    objects = models.Manager()

    class Meta:
        db_table = 'board_column'
        verbose_name = 'board column'
        verbose_name_plural = "board columns"
        ordering = ['column_number']

    @staticmethod
    def get_board_columns(user):
        active_tenant_session = TenantSession.get_active(user)
        if user.is_customer:
            board = Board.objects.get(id=active_tenant_session.tenant.customers_board.id)
        elif user.is_operator:
            board = Board.objects.get(id=active_tenant_session.tenant.operators_board.id)
        elif user.is_developer:
            board = Board.objects.get(id=active_tenant_session.tenant.developers_board.id)
        return BoardColumn.objects.filter(board=board)

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

    objects = models.Manager()

    class Meta:
        db_table = 'transition'
        verbose_name = 'transition'
        verbose_name_plural = 'transitions'
        ordering = ['src_status']

    @property
    def full_transition(self):
        return utils.get_transition_block(self.src_status.color, self.src_status.name, self.dest_status.color, self.dest_status.name)
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

    objects = models.Manager()

    class Meta:
        db_table = 'label'
        verbose_name = 'label'
        verbose_name_plural = 'labels'
        ordering = ['id']

    def __str__(self):
        return str(self.name)


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

    objects = models.Manager()

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
            return utils.get_img_text_field(self.author.icon, self.author, 18, 18)
        except AttributeError:
            return self.author
    author_img_text.fget.short_description = 'Author'

    def __str__(self):
        return self.content

    def __repr__(self):
        return self.content


class Attachment(models.Model):
    id = models.BigAutoField(
        primary_key=True)
    file = models.FileField(
        upload_to=get_upload_path,
        null=True,
        blank=True,
        max_length=1000,
        validators=[validate_file_extension])
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

    objects = models.Manager()

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
        return utils.get_utc_to_local(self.uploaded)
    uploaded_datetime.fget.short_description = 'Uploaded'

    @property
    def display_size(self):
        return utils.get_filesize(self.size)
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
        blank=True,
        null=True,
        auto_now_add=True,
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

    objects = models.Manager()

    class Meta:
        db_table = 'ticket'
        verbose_name = 'ticket'
        verbose_name_plural = 'tickets'
        ordering = ['-updated']

    def save(self, *args, **kwargs):
        if not self.id:
            self.reporter = get_current_user()
            self.slug = self.key.lower()
        self.updated = timezone.now()
        # send_notifications()
        super(Ticket, self).save(*args, **kwargs)

    @property
    def is_service_desk_type(self):
        if self.type.env_type == settings.SD_ENV_TYPE:
            return True
        else:
            return False

    @property
    def is_software_type(self):
        if self.type.env_type == settings.SOFT_ENV_TYPE:
            return True
        else:
            return False

    def get_assignee(self, only_icon=False):
        try:
            if self.assignee is None:
                return utils.get_no_value_info('Unassigned')
            else:
                if only_icon:
                    return utils.get_img_field(self.assignee.icon, self.assignee, 20, 20)
                else:
                    return utils.get_img_text_field(self.assignee.icon, self.assignee, 18, 18)
        except AttributeError:
            return self.assignee
    get_assignee.short_description = 'Assignee'

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Ticket._meta.fields]

    def get_resolution(self):
        if self.resolution is None:
            return utils.get_no_value_info('Unresolved')
        else:
            return self.resolution
    get_resolution.short_description = 'Resolution'

    def getattr(self, field_name):
        return getattr(self, field_name)

    def get_user_field_options(self):
        tenant = self.tenant
        allowed_users = User.objects.filter(groups__name__in=[tenant.customers_group, tenant.operators_group, tenant.developers_group])
        return allowed_users

    def get_initial_status(self):
        if self.type is None:
            raise ValueError('Type cannot be none')
        if self.type.env_type == settings.SD_ENV_TYPE:
            return Status.objects.get(id=settings.SD_INITIAL_STATUS)
        elif self.type.env_type == settings.SOFT_ENV_TYPE:
            return Status.objects.get(id=settings.SOFT_INITIAL_STATUS)
        else:
            return Status.objects.get(id=settings.SD_INITIAL_STATUS)

    def get_transition_options(self, user):
        if user.is_customer and self.is_service_desk_type and not user.is_admin:
            return None
        elif user.is_operator and self.is_software_type and not user.is_admin:
            return None
        elif user.is_developer and self.is_service_desk_type and not user.is_admin:
            return None
        else:
            return TransitionAssociation.objects.filter((Q(transition__src_status=self.status) | Q(transition__src_status__isnull=True)) & Q(type=self.type))

    def get_relation_options(self, user):  # exclude already related tickets from select list and source ticket
        ticket_list_to_relate = []
        for ticket_id in TicketAssociation.objects.filter(src_ticket=self).values_list('dest_ticket'):  # instance -> other ticket
            ticket_list_to_relate.append(int(ticket_id[0]))
        for ticket_id in TicketAssociation.objects.filter(dest_ticket=self).values_list('src_ticket'):  # instance <- other ticket
            ticket_list_to_relate.append(int(ticket_id[0]))
        active_tickets = TenantSession.get_active(user).get_tickets(user, only_open=True).exclude(id=self.id)
        return active_tickets.exclude(id__in=ticket_list_to_relate)

    def get_audit_logs(self):
        return AuditLog.objects.filter(object=self._meta.model.__name__, object_value=self.id)

    @staticmethod
    def get_ordering_fields():
        return [('type', 'Type'), ('key', 'Key'), ('title', 'Title'), ('priority', 'Priority'),
                ('status', 'Status'), ('resolution', 'Resolution'), ('reporter', 'Reporter'),
                ('assignee', 'Assignee'), ('labels', 'Labels'), ('updated', 'Updated'), ('created', 'Created')]

    def get_absolute_url(self):
        pass

    def set_assignee(self, user):
        if user not in self.get_user_field_options() and user is not None:
            return f'Selected user cannot be assigned to <strong>{self}</strong>'
        else:
            self.assignee = user
            self.save()
            logger.info(add_audit_log(self, 'assignee', self.assignee, 'update'))
            if self.assignee is None:
                return f'Ticket <strong>{self}</strong> has been unassigned'
            else:
                return self.assignee

    def set_suspended(self):
        if self.suspended:
            self.suspended = False
        else:
            self.suspended = True
        logger.info(add_audit_log(self, 'suspended', self.suspended, 'update'))
        self.save()
        return self

    def set_status(self, transition_association, context_transition_associations):
        if self.suspended:
            return f'You cannot change status, because <strong>{self}</strong> is suspended'
        for context_transition_association in context_transition_associations:  # check if transition is on the list which was displayed
            if context_transition_association.id == transition_association.id and self.type == transition_association.type:
                self.status = transition_association.transition.dest_status
                self.resolution = transition_association.transition.dest_status.resolution
                self.save()
                logger.info(add_audit_log(self, self.status._meta.model.__name__, self.status, 'update'))
                return self.status
        return f'Transition is not available in <strong>{self}</strong>'

    @staticmethod
    def create_ticket(form, user, files=None):
        tenant = Tenant.get_active(user)
        new_ticket = form.save(commit=False)  # create instance, but do not save
        new_ticket.key = f'{tenant.key}-{tenant.count + 1}'
        new_ticket.tenant = tenant
        new_ticket.status = new_ticket.get_initial_status()
        new_ticket.save()  # create ticket
        logger.info(add_audit_log(new_ticket, new_ticket._meta.model.__name__, new_ticket, 'create'))
        if files:
            for file in files:
                new_ticket.add_attachment(file)
        tenant.count += 1
        tenant.save()
        form.save_m2m()
        return new_ticket

    @staticmethod
    def update_ticket(form):
        ticket_updated = None
        fields = form.initial  # data provided in form
        ticket = form.instance  # ticket data
        for attr in fields:
            attr_value = fields[attr]
            form_attr_value = form.data.get(attr)
            if not ticket_manager.fields_equal(form, attr, attr_value, form_attr_value):
                ticket_updated = ticket.update_field(ticket_updated, attr, form_attr_value, form)
        return ticket_updated

    def update_field(self, ticket_updated, field, field_value, form):
        if ticket_updated is None:
            ticket_updated = self
        try:  # if common field
            setattr(self, field, field_value)
        except ValueError:  # if ForeignKey field
            field_value = form.fields.get(field)._queryset.get(id=field_value)
            setattr(self, field, field_value)
        except TypeError:  # if ManyToMany field
            field_value = form.data.getlist(field)
            self.getattr(field).set(field_value)
            field_value = ', '.join([x.name for x in self.getattr(field).all()])
        finally:
            logger.info(add_audit_log(ticket_updated, field, field_value, 'update'))
            ticket_updated.save()
            return ticket_updated

    def add_attachment(self, attachment):
        new_attachment = Attachment(directory=self.slug)
        new_attachment.file.save(attachment.name, ContentFile(attachment.read()))
        self.attachments.add(new_attachment.id)
        self.save()
        logger.info(add_audit_log(self, new_attachment._meta.model.__name__, new_attachment, 'add'))
        return new_attachment

    def delete_attachment(self, attachment, user):
        attachment_association = AttachmentAssociation.objects.filter(attachment=attachment.id, ticket=self.id)
        if attachment.user.id != user.id and not user.is_admin:
            return f'Attachment not uploaded by you cannot be deleted'
        elif not attachment_association:
            return f'Attachment not exists in <strong>{self}</strong>'
        else:
            attachment_association.delete()
            Attachment.objects.get(id=attachment.id).delete()
            self.save()
            logger.info(add_audit_log(self, attachment._meta.model.__name__, attachment, 'delete'))
            return True

    def add_relation(self, ticket_to_relate, user):
        tickets_allowed_to_relate = []
        for allow_ticket_to_relate in self.get_relation_options(user).values_list('id'):
            tickets_allowed_to_relate.append(str(allow_ticket_to_relate[0]))
        if str(self.id) == ticket_to_relate:
            return f'Ticket cannot have relation with itself'
        elif ticket_to_relate not in tickets_allowed_to_relate:
            return f'Ticket <strong>{self}</strong> cannot be related with selected ticket'
        try:
            related_ticket = Ticket.objects.get(id=ticket_to_relate)
        except Ticket.DoesNotExist:
            return f'Ticket with id <strong>{ticket_to_relate}<strong> does not exist'
        new_relation = TicketAssociation(src_ticket=self, dest_ticket=related_ticket)
        new_relation.save()
        self.save()
        logger.info(add_audit_log(self, related_ticket._meta.model.__name__, related_ticket, 'add'))
        logger.info(add_audit_log(related_ticket, self._meta.model.__name__, self, 'add'))
        return related_ticket

    def delete_relation(self, related_ticket, user):
        try:
            relation = TicketAssociation.objects.get(src_ticket=self, dest_ticket=related_ticket)
        except TicketAssociation.DoesNotExist:
            relation = TicketAssociation.objects.get(src_ticket=related_ticket, dest_ticket=self)
        if not relation:
            return f'Relation not exist in <strong>{self}</strong>'
        elif relation.author.id != user.id and not user.is_admin:
            return f'Relation not added by you cannot be deleted'
        else:
            logger.info(add_audit_log(self, related_ticket._meta.model.__name__, related_ticket, 'delete'))
            self.save()
            related_ticket.save()
            relation.delete()
            return True

    def add_comment(self, content):
        new_comment = Comment(content=content)
        new_comment.save()
        self.save()
        self.comments.add(new_comment)
        logger.info(add_audit_log(self, new_comment._meta.model.__name__, new_comment, 'add'))
        return new_comment

    def delete_comment(self, comment, user):
        comment_association = CommentAssociation.objects.filter(comment=comment.id, ticket=self.id)
        if comment.author.id != user.id and not user.is_admin:
            return f'Comment not added by you cannot be deleted'
        elif not comment_association:
            return f'Comment not exists in <strong>{self}</strong>'
        else:
            comment_association.delete()
            Comment.objects.get(id=comment.id).delete()
            logger.info(add_audit_log(self, comment._meta.model.__name__, comment, 'delete'))
            return True

    def edit_comment(self, comment, content, user):
        comment_association = CommentAssociation.objects.filter(comment=comment.id, ticket=self.id)
        if comment.author.id != user.id and not user.is_admin:
            return f'Comment not added by you cannot be updated'
        elif not comment_association:
            return f'Comment not exists in <strong>{self}</strong>'
        else:
            comment_updated = Comment.objects.get(id=comment.id)
            comment_updated.content = content
            comment_updated.save()
            logger.info(add_audit_log(self, comment._meta.model.__name__, comment, 'update'))
            return comment_updated

    def clone_ticket(self, type_id):  # TO DO
        tenant = self.tenant
        new_ticket = Ticket(
            key=f'{tenant.key}-{tenant.count + 1}',
            tenant=tenant,
            type=type_id,
            description=self.description,
        )
        tenant.count += 1
        tenant.save()
        new_ticket.status = new_ticket.get_initial_status()
        new_ticket.save()  # create ticket
        return new_ticket

    def permission_to_open(self, user):  # to correct
        if self in TenantSession.get_active(user).get_tickets(user) or user.is_admin:
            return True
        else:
            return False

    def permission_to_clone(self, user):
        if user.is_operator or user.is_admin:
            return True
        else:
            return False

    def permission_to_suspend(self, user):
        if user.is_operator and self.is_service_desk_type or user.is_developer and self.is_software_type or user.is_admin:
            return True
        else:
            return False

    def permission_to_assign(self, user):
        if user.is_operator or user.is_developer and self.is_software_type or user.is_admin:
            return True
        else:
            return False

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
    role = models.CharField(
        max_length=25,
        choices=settings.ROLES)

    objects = models.Manager()

    class Meta:
        db_table = 'tenant_session'
        verbose_name = 'tenant session'
        verbose_name_plural = 'tenant sessions'
        ordering = ['id']

    @staticmethod
    def get_active(user):
        try:
            return TenantSession.objects.get(active=True, user=user)
        except TenantSession.DoesNotExist:
            return False

    @staticmethod
    def get_all(user):
        return TenantSession.objects.filter(user=user)

    def get_tickets(self, user, only_open=False):
        tickets = Ticket.objects.filter(tenant=self.tenant)
        if only_open:  # return tickets where resolution is null
            tickets = tickets.filter(tenant=self.tenant, resolution__isnull=True)
        if user.is_customer and not user.is_admin:
            return ticket_manager.filter_tickets(tickets, {'type__env_type': settings.SD_ENV_TYPE})
        # elif user_is_developer(user) and not user.is_admin:
        #    return filter_tickets(tickets, {'type__env_type': settings.SOFT_ENV_TYPE})
        return tickets

    def change_active(self, tenant_id, user):
        self.active = False
        self.save()
        new_active_session = TenantSession.objects.get(tenant=tenant_id, user=user)
        new_active_session.active = True
        new_active_session.save()
        return new_active_session

    def get_user_field_options(self):
        if self.active is not True:
            raise ValueError('Tenant session object need to be active')
        tenant = self.tenant
        allowed_users = User.objects.filter(groups__name__in=[tenant.customers_group, tenant.operators_group, tenant.developers_group])
        return allowed_users

    def __str__(self):
        return f'{self.tenant.key}-{self.user.username}-{self.role}'


class AuditLog(models.Model):  # TO DO - remove message column (convert to function), get representation to content_value, not id even if object
    id = models.BigAutoField(
        primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_user',
        null=True)
    object = models.CharField(
        max_length=55,
        null=True)
    object_value = models.PositiveIntegerField(
        null=True)
    operation = models.CharField(
        max_length=50,
        null=True)
    content = models.CharField(
        max_length=50,
        blank=True,
        null=True)
    content_value = models.CharField(
        max_length=255,
        blank=True,
        null=True)
    ip_address = models.GenericIPAddressField(
        null=True)
    url = models.URLField(
        null=True)
    session = models.CharField(
        max_length=500,
        null=True)
    created = models.DateTimeField(
        auto_now_add=True,
        null=True)

    objects = models.Manager()

    class Meta:
        db_table = 'audit_log'
        verbose_name = 'audit log'
        verbose_name_plural = 'audit logs'
        ordering = ['-created']

    def save(self, *args, **kwargs):
        if not self.id:
            # self.created = timezone.now()
            self.user = get_current_user()
        super(AuditLog, self).save(*args, **kwargs)

    def get_message(self):
        return f'{self.user.username} ({self.ip_address}) {self.get_message_operation()} "{self.content_value}"'

    def get_message_operation(self):
        if self.object == self.content and self.operation != 'create':
            content = f'related {str(self.content).lower()}'
        else:
            content = str(self.content).lower()
        if self.operation == 'create':
            return f'created {content}:'
        elif self.operation == 'delete':
            return f'deleted {content}:'
        elif self.operation == 'update':
            return f'updated {content} to:'
        elif self.operation == 'add':
            return f'added {content}:'
        else:
            return f'changed {str(self.content).lower()} to:'

    def __str__(self):
        return self.get_message()


class BoardColumnAssociation(models.Model):
    column = models.ForeignKey(
        BoardColumn,
        on_delete=models.CASCADE,
        related_name='%(class)s_column_nr')
    status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,
        related_name='%(class)s_status')

    objects = models.Manager()

    class Meta:
        db_table = 'board_column_association'
        verbose_name = 'board column association'
        verbose_name_plural = 'board column associations'
        ordering = ['column']

    @property
    def board_name(self):
        return self.column.board
    board_name.fget.short_description = 'Board'

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

    objects = models.Manager()

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
        return utils.get_transition_block(src_status.color, src_status_name, dest_status.color, dest_status_name)
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
    author = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='%(class)s_author')

    objects = models.Manager()

    class Meta:
        db_table = 'ticket_association'
        verbose_name = 'link'
        verbose_name_plural = 'links'

    def save(self, *args, **kwargs):
        self.author = get_current_user()
        super().save(*args, **kwargs)

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

    objects = models.Manager()

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

    objects = models.Manager()

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

    objects = models.Manager()

    class Meta:
        db_table = 'label_association'

    def __str__(self):
        return f'{self.ticket}-{self.label}'


@receiver(models.signals.post_delete, sender=Attachment)
def auto_delete_file_on_delete(sender, instance, **kwargs):  # Deletes file from filesystem when corresponding `Attachment` object is deleted.
    utils.delete_file(instance)


def add_audit_log(obj, content, content_value, operation):
    request = get_current_request()
    return AuditLog.objects.create(
        user=request.user,
        object=obj._meta.model.__name__,
        object_value=obj.id,
        content=content,
        content_value=content_value,
        operation=operation,
        session=request.session.session_key,
        ip_address=utils.get_client_ip_address(request),
        url=request.path).get_message()
