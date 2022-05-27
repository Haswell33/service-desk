from app.models import Status


def user_tenant_type(request):
    print('categories')
    print(request.user.groups.all())
    # print(Status.objects.filter(name='In progress'))
    # all_status = Tenant.objects.all()
    # print(all_status)
    # print(all_status[0])
    for group in request.user.groups.all():
        print(group.name)
    user_tenant_type = 'developer'
    return {'user_tenant_type': user_tenant_type, 'tenant_id': [1, 2]}
    #return 'dupa'
    # return {'categories': Status.objects.all()}