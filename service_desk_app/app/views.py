from django.http import HttpResponse
import sys
sys.path.insert(0, './html')
from static import login
from .utils import check_if_user_logged


def index(request):
    login.login()
    if not request.user.is_authenticated:
        return HttpResponse('not logged')
    return HttpResponse('logged')


def login(request):
    pass


def test(request):
    return HttpResponse('test')
