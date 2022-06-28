from ..models import Type


def get_type_options(user=None):
    return Type.get_options(user)


def get_initial_type(user=None):
    if user.is_customer:
        return 2  # Service Request
    elif user.is_operator or user.is_developer:
        return 1  # Task
