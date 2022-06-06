import os
from django.conf import settings

CUSTOMER_GROUP_TYPE = 'customer'
OPERATOR_GROUP_TYPE = 'operator'
DEVELOPER_GROUP_TYPE = 'developer'


def get_filename(filename):
    return filename.upper()


def get_img_path():
    return f'{settings.BASE_DIR}{settings.STATIC_URL}images'


def get_img_path_2():
    return f'{settings.STATIC_URL}images'