from ..models import Status


def get_available_status_list(user):
    return Status.get_available_status_list(user)
