from django.http import HttpResponse


def check_if_user_logged(user, curr_page):
    if not user.is_authenticated:
        return HttpResponse('not logged')
