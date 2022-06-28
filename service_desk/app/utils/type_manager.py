from ..models import Type, user_is_developer, user_is_customer, user_is_operator


def get_type_options(user=None):
    return Type.get_options(user)


def get_initial_type(user=None):
    if user_is_customer(user):
        return 2  # Service Request
    elif user_is_operator(user) or user_is_developer(user):
        return 1  # Task
