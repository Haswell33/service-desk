from .utils import get_tenant_by_dev_group, get_tenant_by_cust_group, get_tenant_by_oper_group, json_to_obj
from django.conf import settings
from .models import Tenant
from django.core import serializers
import json


def user_tenant_type(request):
    if len(request.user.groups.all()) == 0:
        print('no groups')
        return request
    else:
        tenants = []
        for group in request.user.groups.all():
            if group.type == settings.CUST_TYPE or group.type == settings.OPER_TYPE or group.type == settings.DEV_TYPE:
                if group.type == settings.CUST_TYPE:
                    tenant = get_tenant_by_cust_group(group)
                elif group.type == settings.OPER_TYPE:
                    tenant = get_tenant_by_oper_group(group)
                elif group.type == settings.DEV_TYPE:
                    tenant = get_tenant_by_dev_group(group)
                if tenant:
                    try:
                        request.session['tenant_type'] = group.type
                        tenant_data = serializers.serialize('json', Tenant.objects.filter(key=tenant.key))
                        if tenant_data not in request.session['tenant']:
                            request.session['tenant'] += tenant_data
                    except KeyError:
                        request.session['tenant'] = tenant_data
                    except IndexError:
                        pass
                tenants_json_str = request.session.get('tenant')[1:-1]
                for tenant_json_str in tenants_json_str.split(']['):
                    tenant_json_obj = json_to_obj(tenant_json_str)
                    #print(tenant_json_obj.model)
                    #print(tenant_json_obj.pk)
                    #print(tenant_json_obj.fields.key)
                    #print(json_object)
                    #for key in json_object:
                    #    print('JSON OBJECT:')
                    #    print(json_object[key])
                    #    print('\n')

            # print(request.session['tenant'])
            # json_object = json.loads(json.dumps([request.session['tenant']]))
            # for key in json_object:
            #    value = json_object(key)
            #    print("The key and value are ({}) = ({})".format(key, value))
        return request


def get_user_icon(request):
    if request.user.is_authenticated:
        request.session['user_icon'] = str(request.user.icon)
    return request


def get_media(request):
    return {'MEDIA_URL': settings.MEDIA_URL}
