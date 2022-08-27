from django.conf import settings
from django.utils.html import mark_safe
from collections import namedtuple
from datetime import timezone
import os
import math
import json
import logging

logger = logging.getLogger(__name__)


def delete_file(obj):
    if obj.file:
        if os.path.isfile(obj.file.path):
            os.remove(obj.file.path)


def get_filesize(size):
    if size == 0:
        return "0B"
    size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    display_size = round(size / p, 2)
    return f'{display_size} {size_names[i]}'


def get_media_path():
    return f'./{settings.MEDIA_URL.strip("/")}'


def get_no_value_info(message):
    return mark_safe(f'<div class="ticket-block_info-left">{message}</div>')


def get_color_box(color, width, height):
    return mark_safe(f'<div style="background: {color}; width: {width}px; height: {height}px; border-radius: 4px;"></div>')


def get_status_color(color, name):
    return mark_safe(f'<div style="background-color: {color};" class="status" title="{name}">{name}</div>')


def get_transition_block(src_status_color, src_status_name, dest_status_color, dest_status_name):
    if src_status_name is not None:
        src_status = get_status_color(src_status_color, src_status_name)
    else:
        src_status = get_no_value_info('All statuses')
    if dest_status_name is not None:
        dest_status = get_status_color(dest_status_color, dest_status_name)
    else:
        dest_status = get_no_value_info('All statuses')
    return mark_safe(f'{src_status}<span class="status-arrow"></span>{dest_status}')


def get_img_field(img, name, height, width):
    return mark_safe(f'<img src="{settings.MEDIA_URL}/{str(img)}" height="{height}" width="{width}" title="{name}" alt={name}/>')


def get_img_text_field(img, name, height, width):
    return mark_safe(f'<div class="img-text_field"><img src="{settings.MEDIA_URL}/{str(img)}" height="{height}" width="{width}" title="{name}" alt={name}/> {name}</div>')


def get_datetime(date):
    return get_utc_to_local(date).strftime('%Y-%m-%d %H:%M:%S')


def get_utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def get_client_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    else:
        return request.META.get('REMOTE_ADDR')


def convert_query_dict_to_dict(query_dict):  # QueryDict -> common python dict
    new_dict = dict()
    for key, value in dict(query_dict).items():
        new_dict[key] = value
    return new_dict


def json_to_obj(data): return json.loads(data, object_hook=_object_hook)
def _object_hook(converted_dict): return namedtuple('X', converted_dict.keys())(*converted_dict.values())
