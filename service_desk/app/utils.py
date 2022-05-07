import os
from django.conf import settings
from django.http import HttpResponse


def check_if_user_logged(user, curr_page):
    if not user.is_authenticated:
        return HttpResponse('not logged')


def get_img_path():
    return os.path.join(settings.STATIC_URL + 'images', 'images')
