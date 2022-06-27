from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from service_desk.app.models import get_media_path
from service_desk.app.utils import get_active_tenant_session
from .managers import CustomUserManager


class ServiceDeskUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=75)
    first_name = models.CharField(
        max_length=75)
    last_name = models.CharField(
        max_length=75)
    display_name = models.CharField(
        max_length=75)
    email = models.EmailField(
        _('email address'),
        unique=True)
    icon = models.ImageField(
        upload_to=f'{get_media_path()}/img/user',
        default=f'img/user/default-avatar.png',
        max_length=500)
    password = models.CharField(
        max_length=500)
    staff = models.BooleanField(
        default=False)
    admin = models.BooleanField(
        default=True)
    active = models.BooleanField(
        default=True)
    created = models.DateTimeField(
        default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    @property
    def user_is_customer(self):
        active_tenant_session = get_active_tenant_session(self)
        if active_tenant_session.user_type == settings.CUST_TYPE:
            return True
        else:
            return False

    @property
    def user_is_operator(self):
        active_tenant_session = get_active_tenant_session(self)
        if active_tenant_session.user_type == settings.OPER_TYPE:
            return True
        else:
            return False

    @property
    def user_is_developer(self):
        active_tenant_session = get_active_tenant_session(self)
        if active_tenant_session.user_type == settings.DEV_TYPE:
            return True
        else:
            return False

    def __str__(self):
        return self.email