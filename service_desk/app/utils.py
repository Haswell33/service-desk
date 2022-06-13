from django.conf import settings
from django.core import serializers
from .models import Tenant, TenantSession, IssueType, Status
from collections import namedtuple
import json
from django.shortcuts import render, reverse, redirect
from django.http import HttpResponseRedirect, HttpResponse


def get_tenant_by_cust_group(group_id):
    try:
        return Tenant.objects.get(customers_group=group_id)
    except Tenant.DoesNotExist:
        return None


def get_tenant_by_oper_group(group_id):
    try:
        return Tenant.objects.get(operators_group=group_id)
    except Tenant.DoesNotExist:
        return None


def get_tenant_by_dev_group(group_id):
    try:
        return Tenant.objects.get(developers_group=group_id)
    except Tenant.DoesNotExist:
        return None


def get_initial_status(env_type):
    if env_type == settings.SD_ENV_TYPE:
        return Status.objects.get(id=settings.SD_INITIAL_STATUS)
    elif env_type == settings.SOFT_ENV_TYPE:
        return Status.objects.get(id=settings.SOFT_INITIAL_STATUS)
    else:
        return Status.objects.get(id=settings.SD_INITIAL_STATUS)


def get_all_user_tenant_sessions(request):
    tenant_sessions = TenantSession.objects.filter(user=request.user.id)
    if tenant_sessions:
        return tenant_sessions
    else:
        return None


def tenant_session(user):
    try:
        TenantSession.objects.filter(user=user)
        return True
    except TenantSession.DoesNotExist:
        return False


def add_tenant_session(tenant, user, user_type):
    TenantSession.objects.create(
        user_type=user_type,
        tenant=tenant,
        user=user)


def tenant_session_exists(tenant, user):
    if TenantSession.objects.filter(tenant=tenant, user=user):
        return True
    else:
        return False


def activate_tenant(tenant, request, user):
    tenant_cookie = f'active_tenant_id_{str(user.id)}'
    if request.COOKIES.get(tenant_cookie) is None and not TenantSession.objects.filter(active=True, user=user):
        set_active_tenant(tenant, user)
    elif request.COOKIES.get(tenant_cookie) == str(tenant.id):
        set_active_tenant(tenant, user)


def set_active_tenant(tenant, user):
    tenant_session = TenantSession.objects.get(tenant=tenant, user=user)
    tenant_session.active = True
    tenant_session.save()


def get_env_type(issue_type_id): return IssueType.objects.get(id=issue_type_id).env_type
def get_active_tenant(user): return Tenant.objects.get(id=get_active_tenant_session(user).tenant.id)
def get_active_tenant_session(user): return TenantSession.objects.get(active=True, user=user)
def clear_tenant_session(user): TenantSession.objects.filter(user=user).delete()
def json_to_obj(data): return json.loads(data, object_hook=_object_hook)
def _object_hook(converted_dict): return namedtuple('X', converted_dict.keys())(*converted_dict.values())




