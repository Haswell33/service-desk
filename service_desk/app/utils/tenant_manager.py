from django.conf import settings
from ..models import Tenant, TenantSession


def get_tenant_cookie_name(user=None):
    return Tenant.get_cookie_name(user)


def get_active_tenant_session(user=None):
    return TenantSession.get_active(user)


def get_all_user_tenant_sessions(user=None):  # limited for user which executed function
    return TenantSession.get_all(user)


def get_active_tenant(user=None):
    return Tenant.get_active(user)


def get_tenant_by_role(role, group_id):
    try:
        if role == settings.CUST_TYPE:
            return Tenant.objects.get(customers_group=group_id)
        elif role == settings.OPER_TYPE:
            return Tenant.objects.get(operators_group=group_id)
        elif role == settings.DEV_TYPE:
            return Tenant.objects.get(developers_group=group_id)
    except Tenant.DoesNotExists:
        return None


def active_session_exists(user=None):  # checks if any active tenant session exists for specific user
    try:
        get_active_tenant_session(user)
        return True
    except TenantSession.DoesNotExist:
        return False


def tenant_session(user):  # checks if any tenant session exists for specific user
    try:
        TenantSession.objects.filter(user=user)
        return True
    except TenantSession.DoesNotExist:
        return False


def clear_tenant_session(user):  # delete all tenant session data for selected user (e.g. during log out)
    TenantSession.objects.filter(user=user).delete()


def get_active_tenant_tickets(user=None, only_open=False):  # filtered by correct role
    active_tenant_session = TenantSession.get_active(user)
    return active_tenant_session.get_tickets(user, only_open)
