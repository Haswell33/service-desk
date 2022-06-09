from .utils import get_tenant_by_dev_group, get_tenant_by_cust_group, get_tenant_by_oper_group
from django.conf import settings
from django.core import serializers


def user_tenant_type(request):
    if len(request.user.groups.all()) == 0:
        print('no groups')
        return request
    else:
        for group in request.user.groups.all():
            if group.type == settings.CUST_TYPE or group.type == settings.OPER_TYPE or group.type == settings.DEV_TYPE:
                print(group.type)
                if group.type == settings.CUST_TYPE:
                    tenant = get_tenant_by_cust_group(group)
                elif group.type == settings.OPER_TYPE:
                    tenant = get_tenant_by_oper_group(group)
                elif group.type == settings.DEV_TYPE:
                    tenant = get_tenant_by_dev_group(group.id)
                if tenant:
                    try:
                        request.session['tenant_key'] = tenant.key
                        request.session['tenant_name'] = tenant.name
                        request.session['tenant_type'] = group.type
                        request.session['tenant_icon'] = '../' + str(tenant.icon)
                        request.session['tenant_board'] = str(tenant.developers_board)
                    except IndexError:
                        pass
        return request


def get_user_icon(request):
    if request.user.is_authenticated:
        request.session['user_icon'] = str(request.user.icon)
    return request
