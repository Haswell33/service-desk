from .utils import get_tenant_by_group_type, add_tenant_session, tenant_session_exists, set_active_tenant, get_all_user_tenant_sessions, get_active_tenant_session
from django.conf import settings


def context_tenant_session(request):
    if len(request.user.groups.all()) == 0:
        return request
    else:
        for group in request.user.groups.all():
            if group.type == settings.CUST_TYPE or group.type == settings.OPER_TYPE or group.type == settings.DEV_TYPE:
                tenant = get_tenant_by_group_type(group.type, group)
                if tenant and not tenant_session_exists(tenant, request.user):
                    add_tenant_session(tenant, request.user, group.type)  # add record to database with information about available tenant
                    set_active_tenant(tenant, request)  # check if in django sessions is already activated any tenant
        return request


def get_user_icon(request):
    if request.user.is_authenticated:
        request.session['user_icon'] = str(request.user.icon)
    return request


def get_media(request):
    return {'MEDIA_URL': settings.MEDIA_URL}


def get_tenants(request):
    if request.user.is_authenticated:
        return {'tenant_sessions': get_all_user_tenant_sessions(request.user), 'active_tenant_session': get_active_tenant_session(request.user)}
    return request

