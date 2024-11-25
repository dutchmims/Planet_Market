# ruff: noqa

from django.shortcuts import render

def index(request):

    return render(request, 'home/index.html')

def custom_page_not_found_view(request, exception):

    return render(request, '404.html', status=404)
