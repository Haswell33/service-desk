from django.dispatch import receiver
from django.db import models
from .context_processors import context_tenant_session
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from .utils import util_manager, tenant_manager
from .models import Attachment
from logging import getLogger

log = getLogger('core.receivers')


@receiver(models.signals.post_delete, sender=Attachment)
def auto_delete_file_on_delete(sender, instance, **kwargs):  # Deletes file from filesystem when corresponding `Attachment` object is deleted.
    util_manager.delete_file(instance)


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    log.info(f'user {user.username} [{util_manager.get_client_ip_address(request)}] logged in')


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    log.info(f'user {user.username} [{util_manager.get_client_ip_address(request)}] logged out')


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, **kwargs):
    log.info(f"login failed for '{credentials.get('username', None)}' username")


def after_logout(sender, user, request, **kwargs):
    tenant_manager.clear_tenant_session(user)


def after_login(sender, user, request, **kwargs):
    if not tenant_manager.tenant_session(user):
        context_tenant_session(request)
