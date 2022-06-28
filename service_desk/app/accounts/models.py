from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from ..utils import utils
from .managers import CustomUserManager
from django.contrib.auth.models import User, Group


class ServiceDeskUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=75,
        unique=True)
    first_name = models.CharField(
        max_length=75)
    last_name = models.CharField(
        max_length=75)
    display_name = models.CharField(
        max_length=75)
    email = models.EmailField(
        _('email address'))
    icon = models.ImageField(
        upload_to=f'{utils.get_media_path()}/img/user',
        default=f'img/user/default-avatar.png',
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
        to='auth.Group')
    user_permissions = models.ManyToManyField(
        related_query_name='user',
        related_name='user_set',
        to='auth.Permission')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        db_table = 'user'
        verbose_name = 'user'
        verbose_name_plural = 'users'

    @property
    def is_customer(self):
        from ..models import TenantSession
        if TenantSession.get_active(self).role == settings.CUST_TYPE:
            return True
        else:
            return False

    @property
    def is_operator(self):
        from ..models import TenantSession
        if TenantSession.get_active(self).role == settings.OPER_TYPE:
            return True
        else:
            return False

    @property
    def is_developer(self):
        from ..models import TenantSession
        if TenantSession.get_active(self).role == settings.DEV_TYPE:
            return True
        else:
            return False

    def __str__(self):
        from ..models import TenantSession
        if TenantSession.get_active(self).role == settings.DEV_TYPE:
            return True
        else:
            return False
