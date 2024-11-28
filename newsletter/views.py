"""Newsletter views."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from mailchimp_marketing.api_client import ApiClientError # type: ignore
from .forms import NewsletterForm
from .models import Subscriber
from .utils import get_mailchimp_client
import hashlib


def mailchimp_ping_view(request):
    response = get_mailchimp_client().ping.get()
    return JsonResponse(response)

def subscribe(request):
    """Handle newsletter subscription."""
    form = NewsletterForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data['email']
        if email:
            try:
                # Create Mailchimp client
                mailchimp_client = get_mailchimp_client()
                list_id = settings.MAILCHIMP_LIST_ID

                # Add subscriber to Mailchimp
                mailchimp_client.lists.add_list_member(list_id, {
                    "email_address": email,
                    "status": "subscribed"
                })

                # Create local subscriber record
                subscriber = Subscriber.objects.create(
                    email=email,
                    email_hash=hashlib.md5(email.encode()).hexdigest(),
                    is_active=True
                )
                subscriber.save()

                return redirect('subscribe_success')

            except ApiClientError as error:

                return redirect('subscribe_fail')
        else:
            messages.error(request, 'Please provide a valid email address.')

    return render(request, 'newsletter/subscribe.html', {'form': form})

def unsubscribe_form(request):
    """Handle newsletter unsubscription."""
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                # Try to find subscriber
                subscriber = Subscriber.objects.filter(email=email).first()
                
                if not subscriber:
                    messages.error(request, 'This email address is not subscribed to our newsletter.')
                    return render(request, 'newsletter/unsubscribe_form.html')

                # Update Mailchimp
                client = get_mailchimp_client()
                try:
                    client.lists.update_list_member(
                        settings.MAILCHIMP_LIST_ID,
                        subscriber.email_hash,
                        {"status": "unsubscribed"}
                    )
                except ApiClientError:
                    # If the email doesn't exist in Mailchimp, just update our local record
                    pass

                # Update local record
                subscriber.is_active = False
                subscriber.save()

                return redirect('unsubscribe_success')

            except Exception as e:
                messages.error(request, 'An error occurred while processing your request. Please try again later.')
                return redirect('unsubscribe_fail')

        else:
            messages.error(request, 'Please provide a valid email address.')

    return render(request, 'newsletter/unsubscribe_form.html')

# ---

def subscribe_success(request):
    """Handle successful subscription."""
    return render(request, 'newsletter/message.html', {
        'title': 'Subscription Successful',
        'message': 'Thank you for subscribing to our newsletter!',
        'status': 'success'
    })

def subscribe_fail(request):
    """Handle failed subscription."""
    return render(request, 'newsletter/message.html', {
        'title': 'Subscription Failed',
        'message': 'Sorry, there was an error processing your subscription. Please try again later.',
        'status': 'error'
    })

def unsubscribe_success(request):
    """Handle successful unsubscription."""
    return render(request, 'newsletter/message.html', {
        'title': 'Unsubscribe Successful',
        'message': 'You have been successfully unsubscribed from our newsletter.',
        'status': 'success'
    })

def unsubscribe_fail(request):
    """Handle failed unsubscription."""
    return render(request, 'newsletter/message.html', {
        'title': 'Unsubscribe Failed',
        'message': 'Sorry, there was an error processing your unsubscription. Please try again later.',
        'status': 'error'
    })