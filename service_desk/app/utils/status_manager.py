from ..models import Status


def get_available_status_list(user=None):
    return Status.get_available_status_list(user)
