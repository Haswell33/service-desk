from app.models import Status, Tenant, Group
from . import utils
from django.core import serializers
from django.forms.models import model_to_dict


def user_tenant_type(request):
    if len(request.user.groups.all()) == 0:
        print('no groups')
        return request
    else:
        for group in request.user.groups.all():
            id = 1
            if group.type == utils.CUSTOMER_GROUP_TYPE:
                request.session['tenant_key'] = Tenant.objects.filter(customers_group=group.id).values('key')[0]['key']
                request.session['tenant_name'] = Tenant.objects.filter(customers_group=group.id).values('name')[0]['name']
                request.session['tenant_type'] = group.type
                request.session['tenant_icon'] = '../' + Tenant.objects.filter(customers_group=group.id).values('icon')[0]['icon']
                request.session['tenant_board'] = Tenant.objects.filter(customers_group=group.id).values('customers_group')[0]['customers_group']
            elif group.type == utils.OPERATOR_GROUP_TYPE:
                request.session['tenant_key'] = Tenant.objects.filter(operators_group=group.id).values('key')[0]['key']
                request.session['tenant_name'] = Tenant.objects.filter(operators_group=group.id).values('name')[0]['name']
                request.session['tenant_type'] = group.type
                request.session['tenant_icon'] = '../' + Tenant.objects.filter(operators_group=group.id).values('icon')[0]['icon']
                request.session['tenant_board'] = Tenant.objects.filter(operators_group=group.id).values('operators_group')[0]['operators_group']
            elif group.type == utils.DEVELOPER_GROUP_TYPE:
                request.session['tenant_key'] = Tenant.objects.filter(developers_group=group.id).values('key')[0]['key']
                request.session['tenant_name'] = Tenant.objects.filter(developers_group=group.id).values('name')[0]['name']
                request.session['tenant_type'] = group.type
                request.session['tenant_icon'] = '../' + Tenant.objects.filter(developers_group=group.id).values('icon')[0]['icon']
                request.session['tenant_board'] = Tenant.objects.filter(developers_group=group.id).values('developers_group')[0]['developers_group']
        # print(request)
        return request
