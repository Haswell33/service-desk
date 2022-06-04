import os
from django.conf import settings
from django.http import HttpResponse

CUSTOMER_GROUP_TYPE = 'customer'
OPERATOR_GROUP_TYPE = 'operator'
DEVELOPER_GROUP_TYPE = 'developer'


def check_if_user_logged(user, curr_page):
    if not user.is_authenticated:
        return HttpResponse('not logged')


def get_img_path():
    return f'{settings.BASE_DIR}{settings.STATIC_URL}images'


def get_img_path_2():
    return f'{settings.STATIC_URL}images'