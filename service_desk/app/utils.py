from django.conf import settings

CUSTOMER_GROUP_TYPE = 'customer'
OPERATOR_GROUP_TYPE = 'operator'
DEVELOPER_GROUP_TYPE = 'developer'


def get_filename(filename):
    return filename.upper()


def get_media_path():
    return f'{settings.MEDIA_URL.strip("/")}'
