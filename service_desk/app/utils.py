import os
from django.conf import settings
from django.http import HttpResponse


def check_if_user_logged(user, curr_page):
    if not user.is_authenticated:
        return HttpResponse('not logged')


def get_user_type(request):
    for group in request.user.groups.all():
        print(group.name)
    return 'dupa'


def get_img_path():
    return f'{settings.BASE_DIR}{settings.STATIC_URL}images'


def get_img_path_2():
    return f'{settings.STATIC_URL}images'