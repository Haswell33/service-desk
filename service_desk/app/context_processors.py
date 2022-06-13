from .utils import get_tenant_by_dev_group, get_tenant_by_cust_group, get_tenant_by_oper_group, add_tenant_session, tenant_session_exists, activate_tenant, get_all_user_tenant_sessions
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect, HttpResponse


def context_tenant_session(request):
    if len(request.user.groups.all()) == 0:
        print('no groups')
        return request
    else:
        for group in request.user.groups.all():
            if group.type == settings.CUST_TYPE or group.type == settings.OPER_TYPE or group.type == settings.DEV_TYPE:
                if group.type == settings.CUST_TYPE:
                    tenant = get_tenant_by_cust_group(group)
                elif group.type == settings.OPER_TYPE:
                    tenant = get_tenant_by_oper_group(group)
                elif group.type == settings.DEV_TYPE:
                    tenant = get_tenant_by_dev_group(group)
                if tenant:
                    if not tenant_session_exists(tenant, request.user):
                        add_tenant_session(tenant, request.user, group.type)  # add record to database with information about available tenant
                        activate_tenant(tenant, request, request.user)  # check if in django sessions is already activated any tenant
        return request


def get_user_icon(request):
    if request.user.is_authenticated:
        request.session['user_icon'] = str(request.user.icon)
    return request


def get_media(request):
    return {'MEDIA_URL': settings.MEDIA_URL}


def get_tenant_sessions(request):
    tenant_sessions = get_all_user_tenant_sessions(request)
    return {'tenant_sessions': tenant_sessions}
