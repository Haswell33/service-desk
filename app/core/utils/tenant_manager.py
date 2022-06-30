from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from ..models import Tenant, TenantSession


def get_tenant_cookie_name(user):
    return Tenant.get_cookie_name(user)


def get_active_tenant_session(user):
    return TenantSession.get_active(user)


def get_all_tenant_sessions(user):  # limited for user which executed function
    return TenantSession.get_all(user)


def get_active_tenant(user):
    return Tenant.get_active(user)


def get_tenant_by_role(role, group_id):
    try:
        if role == settings.CUST_TYPE:
            return Tenant.objects.get(customers_group=group_id)
        elif role == settings.OPER_TYPE:
            return Tenant.objects.get(operators_group=group_id)
        elif role == settings.DEV_TYPE:
            return Tenant.objects.get(developers_group=group_id)
    except ObjectDoesNotExist:
        return None


def active_session_exists(user):  # checks if any active tenant session exists for specific user
    if get_active_tenant_session(user):
        return True
    else:
        return False


def tenant_session(user):  # checks if any tenant session exists for specific user
    try:
        TenantSession.objects.filter(user=user)
        return True
    except ObjectDoesNotExist:
        return False


def clear_tenant_session(user):  # delete all tenant session data for selected user (e.g. during log out)
    TenantSession.objects.filter(user=user).delete()


def get_active_tenant_tickets(user, only_open=False):  # filtered by correct role
    active_tenant_session = TenantSession.get_active(user)
    return active_tenant_session.get_tickets(user, only_open)
