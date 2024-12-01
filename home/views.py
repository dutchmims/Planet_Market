from django.shortcuts import render


def index(request):
    """A view to return the index page"""
    return render(request, 'home/index.html')


def custom_page_not_found_view(request, exception):
    """Custom 404 page"""
    return render(request, 'errors/404.html', status=404)
