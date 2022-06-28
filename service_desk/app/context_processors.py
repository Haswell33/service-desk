from .utils import tenant_manager
from django.conf import settings


def context_tenant_session(request):
    if len(request.user.groups.all()) == 0:
        return request
    else:
        for group in request.user.groups.all():
            if group.role == settings.CUST_TYPE or group.role == settings.OPER_TYPE or group.role == settings.DEV_TYPE:
                tenant = tenant_manager.get_tenant_by_role(group.role, group)
                if tenant and not tenant.session_exists(request.user):
                    tenant.add_session(group.role, request.user)  # add record to database with information about available tenant
                    tenant.set_active_session(request)  # check if in django sessions is already activated any tenant
        return request


def get_user_icon(request):
    if request.user.is_authenticated:
        request.session['user_icon'] = str(request.user.icon)
    return request


def get_media(request):
    return {'MEDIA_URL': settings.MEDIA_URL}


def get_tenants(request):
    if request.user.is_authenticated:
        return {
            'tenant_sessions': tenant_manager.get_all_user_tenant_sessions(request.user),
            'active_tenant_session': tenant_manager.get_active_tenant_session(request.user)}
    return request

