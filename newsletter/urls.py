"""Newsletter URL patterns."""

from django.urls import path
from . import views

urlpatterns = [
    path('ping/', views.mailchimp_ping_view),  # new
    path('subscribe/', views.subscribe, name='subscribe'),
    path('subscribe-success/', views.subscribe_success, name='subscribe_success'),
    path('subscribe-fail/', views.subscribe_fail, name='subscribe_fail'),
    path('unsubscribe-form/', views.unsubscribe_form, name='unsubscribe_form'),
    path('unsubscribe-success/', views.unsubscribe_success, name='unsubscribe_success'),
    path('unsubscribe-fail/', views.unsubscribe_fail, name='unsubscribe_fail'),
]