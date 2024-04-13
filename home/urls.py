from django.urls import path
from . import views

# Import the custom 404 view function
from .views import custom_page_not_found_view

urlpatterns = [
    path('', views.index, name='home'),
]

# Set the custom 404 error handler
handler404 = 'home.views.custom_page_not_found_view'
