"""Newsletter views."""

from django.shortcuts import (render,
                            redirect,
                            get_object_or_404)
from django.conf import settings
from django.http import JsonResponse
from mailchimp_marketing.api_client import (
    ApiClientError)  # type: ignore
from .forms import NewsletterForm
from .models import Subscriber
from .utils import (get_mailchimp_client,
                log_message,
                generate_email_hash)
import hashlib


def mailchimp_ping_view(request):
    """Test Mailchimp API connection."""
    try:
        response = get_mailchimp_client().ping.get()
        log_message(
            "Mailchimp API ping successful",
            "INFO")
        return JsonResponse(response)
    except Exception as error:
        log_message(
            "Mailchimp API ping failed", "ERROR", error)
        return JsonResponse(
            {"error": "Failed to ping Mailchimp API"},
            status=500)


def subscribe(request):
    """Handle newsletter subscription."""
    form = NewsletterForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data['email']
        try:
            mailchimp_client = get_mailchimp_client()
            list_id = settings.MAILCHIMP_LIST_ID

            # Add subscriber to Mailchimp
            mailchimp_client.lists.\
                add_list_member(list_id, {
                "email_address": email,
                "status": "subscribed"
            })

            # Create local subscriber record
            subscriber = Subscriber.objects.create(
                email=email,
                email_hash=hashlib.md5(
                    email.encode()).hexdigest(),
                is_active=True
            )
            subscriber.save()
            log_message(
                f"""Successfully subscribed
                {email} to {list_id}""",
                "INFO"
            )
            return redirect('subscribe_success')

        except ApiClientError as error:
            error_msg = str(error.text) if \
                hasattr(error, 'text')\
                else str(error)

            if "Resource Not Found" in error_msg:
                log_message(
                    f"Invalid list ID: {list_id}",
                    "ERROR",
                    error
                )
                raise ApiClientError(
                    "Invalid list ID") \
                    from error
            if "Member Exists" in error_msg:
                log_message(
                    f"Member already exists: {email}",
                    "WARNING",
                    error
                )
                raise ApiClientError(
                    "Member already subscribed")\
                    from error
            if "Invalid Resource" in error_msg:
                log_message(
                    f"Invalid email format: {email}",
                    "ERROR",
                    error
                )
                raise ApiClientError(
                    "Invalid email format")\
                    from error
            log_message(
                f"Subscription error for {email}",
                "ERROR",
                error
            )

            return redirect('subscribe_fail')

    return render(request, 'newsletter/subscribe.html',
                {'form': form})


def unsubscribe_form(request):
    """Handle newsletter unsubscription."""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            mailchimp_client = get_mailchimp_client()
            list_id = settings.MAILCHIMP_LIST_ID
            subscriber_hash = generate_email_hash(email)

            # Check if already unsubscribed
            try:
                member = mailchimp_client.\
                    lists.get_list_member(
                        list_id, subscriber_hash)
                if member['status'] == 'unsubscribed':
                    log_message(
                        "Member already unsubscribed:"
                        + f" {email}",
                        "WARNING"
                    )
                    return redirect('unsubscribe_success')
            except ApiClientError as error:
                if "Resource Not Found" in str(error.text):
                    log_message(
                        f"Member not found: {email}",
                        "WARNING",
                        error
                    )
                    return redirect('unsubscribe_fail')
                raise

            # Unsubscribe from Mailchimp
            mailchimp_client.lists.update_list_member(
                list_id,
                subscriber_hash,
                {"status": "unsubscribed"}
            )

            # Update local record
            subscriber = get_object_or_404(
                Subscriber,
                email_hash=subscriber_hash)
            subscriber.is_active = False
            subscriber.save()

            log_message(
                "Successfully unsubscribed {email} " +
                f"from {list_id}",
                "INFO"
            )
            return redirect('unsubscribe_success')

        except ApiClientError as error:
            log_message(
                f"Failed to unsubscribe {email}",
                "ERROR",
                error
            )
            return redirect('unsubscribe_fail')
        except Exception as error:
            log_message(
                f"Unexpected error unsubscribing {email}",
                "ERROR",
                error
            )
            return redirect('unsubscribe_fail')

    return render(request, 'newsletter/unsubscribe_form.html')


def subscribe_success(request):
    """Handle successful subscription."""
    log_message("Subscription success page viewed", "INFO")
    context = {
        'title': 'Subscription Successful',
        'message': 'You have been successfully subscribed to our newsletter.',
        'status': 'success'
    }
    return render(request, 'newsletter/message.html', context)


def subscribe_fail(request):
    """Handle failed subscription."""
    log_message("Subscription failure page viewed", "WARNING")
    context = {
        'title': 'Subscription Failed',
        'message': 'There was an error processing your subscription. Please try again.',
        'status': 'error'
    }
    return render(request, 'newsletter/message.html', context)


def unsubscribe_success(request):
    """Handle successful unsubscription."""
    log_message("Unsubscription success page viewed", "INFO")
    context = {
        'title': 'Unsubscription Successful',
        'message': 'You have been successfully unsubscribed from our newsletter.',
        'status': 'success'
    }
    return render(request, 'newsletter/message.html', context)


def unsubscribe_fail(request):
    """Handle failed unsubscription."""
    log_message("Unsubscription failure page viewed", "WARNING")
    context = {
        'title': 'Unsubscription Failed',
        'message': 'There was an error processing your unsubscription. Please try again.',
        'status': 'error'
    }
    return render(request, 'newsletter/message.html', context)