from django.conf import settings
from .models import Tenant, TenantSession, IssueType, Status
import json
from collections import namedtuple


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


def get_session_tenant_deserialized(request):
    #print(request.session.get('tenant'))

    #data = serializers.deserialize(request.session.get('tenant'), 'json')
    #dict_str = request.session.get('tenant')[0]
    #dict_list = request.session.get('tenant')[1:-1]
    #j = [json.loads(i) for i in dict_list]
    #for key in j:
    #    print(j[key])
    return request


#def get_active_tenant_issues(request):
#    return request


def get_initial_status(env_type):
    if env_type == settings.SD_ENV_TYPE:
        return Status.objects.get(id=settings.SD_INITIAL_STATUS)
    elif env_type == settings.SOFT_ENV_TYPE:
        return Status.objects.get(id=settings.SOFT_INITIAL_STATUS)
    else:
        return Status.objects.get(id=settings.SD_INITIAL_STATUS)


def tenant_data_in_session(request):
    try:
        request.session.get('tenant')
        return True
    except ValueError:
        return False


#def change_status():
#    pass

def get_env_type(issue_type_id): return IssueType.objects.get(id=issue_type_id).env_type
def get_session_tenant_type(request): return request.session.get('tenant_type')
def get_tenant(request): return Tenant.objects.get(key=request.session.get('tenant_key'))
def clear_tenant_session(user): TenantSession.objects.get(user=user).delete()
def json_to_obj(data): return json.loads(data, object_hook=_object_hook)
def _object_hook(converted_dict): return namedtuple('X', converted_dict.keys())(*converted_dict.values())
