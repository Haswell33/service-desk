from django import template

register = template.Library()


@register.filter
def in_list(value, list_data):
    if str(value) in list_data:
        return True
    else:
        return False


@register.simple_tag
def get_verbose_name(object, field_name):
    return object._meta.get_field(field_name).verbose_name


@register.simple_tag
def get_name(object, field_name):
    return object._meta.get_field(field_name).name


@register.simple_tag
def get_help_text(object, field_name):
    return object._meta.get_field(field_name).help_text