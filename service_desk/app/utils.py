from django.conf import settings
from .models import Tenant, IssueType, Status


def get_filename(filename):
    return filename.upper()


def get_tenant(request):
    return Tenant.objects.get(key=request.session.get('tenant_key'))


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


def get_session_tenant_type(request):
    return request.session.get('tenant_type')


def get_env_type(issue_type_id):
    return IssueType.objects.filter(id=issue_type_id).values('env_type')[0]['env_type']


def get_initial_status(env_type):
    if env_type == settings.SD_ENV_TYPE:
        return Status.objects.get(id=settings.SD_INITIAL_STATUS)
    elif env_type == settings.SOFT_ENV_TYPE:
        return Status.objects.get(id=settings.SOFT_INITIAL_STATUS)
    else:
        return Status.objects.get(id=settings.SD_INITIAL_STATUS)
