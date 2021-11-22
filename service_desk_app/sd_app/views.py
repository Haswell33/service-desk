from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse('HOMEPAGE')


def test(request):
    return HttpResponse("test")
