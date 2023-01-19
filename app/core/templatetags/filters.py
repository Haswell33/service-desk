import timeago
from django import template
from datetime import datetime
from django.conf import settings
from ..utils import util_manager

register = template.Library()


@register.filter
def in_list(value, list_data):
    if str(value) in list_data:
        return True
    else:
        return False


@register.simple_tag
def get_verbose_name(obj, field_name):
    return obj._meta.get_field(field_name).verbose_name


@register.simple_tag
def get_name(obj, field_name):
    return obj._meta.get_field(field_name).name


@register.simple_tag
def get_help_text(obj, field_name):
    return obj._meta.get_field(field_name).help_text


@register.simple_tag
def get_file_extension_class(filename):
    filename_extension = filename.split('.')[-1]
    file_extensions = settings.FILE_EXTENSIONS
    for file_extension in file_extensions:
        extension_list = file_extensions[file_extension]
        for extension in extension_list:
            if extension == filename_extension:
                return file_extension
    return 'default'


@register.simple_tag
def get_max_length_string(string, max_length):
    if len(string) >= max_length:
        return f'{string[:max_length]}...'
    else:
        return string


@register.simple_tag
def get_time_ago(date):
    now = datetime.now()
    date = util_manager.get_utc_to_local(date)
    date_converted = date.strftime('%Y-%m-%d %H:%M:%S')
    return timeago.format(date_converted, now, 'en')


@register.simple_tag()
def get_datetime_local(date):
    return util_manager.get_datetime(date)


@register.simple_tag()
def call_method(obj, method_name, *args):
    method = getattr(obj, method_name)
    return method(*args)
