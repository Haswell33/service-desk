from .utils import get_tenant_by_dev_group, get_tenant_by_cust_group, get_tenant_by_oper_group, get_tenant_serialized
from django.conf import settings


class test:
    def process_request(self, request):
        """
        Determine the organization based on the subdomain
        """
        if len(request.user.groups.all()) == 0:
            print('no groups')
            return request
        else:
            for group in request.user.groups.all():
                print(group.name)
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
                            tenant_data = get_tenant_serialized(tenant.key)
                            try:
                                if tenant_data not in request.session['tenant']:
                                    request.session['tenant'] += tenant_data
                                # print(request.session['tenant'])
                                # json_object = json.loads(json.dumps([request.session['tenant']]))
                                # for key in json_object:
                                #    value = json_object(key)
                                #    print("The key and value are ({}) = ({})".format(key, value))
                            except KeyError:
                                request.session['tenant'] = tenant_data
                        except IndexError:
                            pass
            return request
