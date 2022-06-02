from app.models import Status, Tenant, Group
from . import utils
from django.core import serializers
from django.forms.models import model_to_dict


def user_tenant_type(request):
    tenants = {}
    for group in request.user.groups.all():
        id = 1
        if group.type == utils.CUSTOMER_GROUP_TYPE:
            '''tenants[Tenant.objects.filter(customers_group=group.id).values('name')[0]['name']] = dict(
                tenant_type=group.type,
                icon=Tenant.objects.filter(customers_group=group.id).values('icon')[0]['icon'],
                board=Tenant.objects.filter(customers_group=group.id).values('customers_group')[0]['customers_group'])'''
            # request.session['tenant_name'] = Tenant.objects.filter(customers_group=group.id).values('name')[0]['name']
            # request.session['tenant_type'] = group.type
            # request.session['tenant_icon'] = Tenant.objects.filter(customers_group=group.id).values('icon')[0]['icon']
            # request.session['tenant_board'] = Tenant.objects.filter(customers_group=group.id).values('customers_group')[0]['customers_group']
            request.session['tenant' + str(id)] = dict(
                key='dupa',
                name=Tenant.objects.filter(customers_group=group.id).values('name')[0]['name'],
                tenant_type=group.type,
                icon=Tenant.objects.filter(customers_group=group.id).values('icon')[0]['icon'],
                board=Tenant.objects.filter(customers_group=group.id).values('customers_group')[0]['customers_group'])
        elif group.type == utils.OPERATOR_GROUP_TYPE:
            '''tenants[Tenant.objects.filter(operators_group=group.id).values('name')[0]['name']] = dict(
                tenant_type=group.type,
                icon=Tenant.objects.filter(operators_group=group.id).values('icon')[0]['icon'],
                board=Tenant.objects.filter(operators_group=group.id).values('operators_group')[0]['operators_group'])'''
            request.session['tenant'] = dict(
                key=Tenant.objects.filter(operators_group=group.id).values('name')[0]['name'],
                tenant_type=group.type,
                icon=Tenant.objects.filter(operators_group=group.id).values('icon')[0]['icon'],
                board=Tenant.objects.filter(operators_group=group.id).values('operators_group')[0]['operators_group'])
        elif group.type == utils.DEVELOPER_GROUP_TYPE:
            tenants[Tenant.objects.filter(developers_group=group.id).values('name')[0]['name']] = dict(
                tenant_type=group.type,
                icon=Tenant.objects.filter(developers_group=group.id).values('icon')[0]['icon'],
                board=Tenant.objects.filter(developers_group=group.id).values('developers_group')[0]['developers_group'])
    if any(tenants):
        print(tenants)
    else:
        print('no tenant associated')
    print(request)
    return {'tenant': tenants}
