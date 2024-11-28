"""Newsletter utility functions."""

import hashlib
import os
from datetime import datetime
from django.conf import settings
from mailchimp_marketing.api_client import ApiClientError # type: ignore
import mailchimp_marketing as MailchimpMarketing # type: ignore

# Setup log file with timestamp
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f'newsletter_{datetime.now().strftime("%Y%m%d")}.log')



def log_message(message, level="INFO", error=None):
    """Log a message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {level}: {message}"
    if error:
        log_entry += f"\nError details: {str(error)}"
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry + "\n")
    print(log_entry)  # For development/debug

def get_mailchimp_client():
    """Get configured Mailchimp client with error handling.
    """

    try:
        client = MailchimpMarketing.Client()
        client.set_config({
            "api_key": settings.MAILCHIMP_API_KEY,
            "server": settings.MAILCHIMP_REGION
        })

        # Verify credentials with a ping
        client.ping.get()
        return client

    except ApiClientError as error:
        error_msg = str(error.text) if hasattr(error, 'text') else str(error)
        if "API Key Invalid" in error_msg:
            log_message("Invalid Mailchimp API key", "ERROR", error)
            raise ApiClientError("Invalid API credentials")
        elif "Invalid datacenter" in error_msg:
            log_message("Invalid Mailchimp server region", "ERROR", error)
            raise ApiClientError("Invalid server configuration")
        else:
            log_message("Mailchimp client configuration error", "ERROR", error)
            raise

def generate_email_hash(email):
    """Generate a hash for the email address.

    Args:
        email (str): Email address to hash

    Returns:
        str: MD5 hash of the email address
    """

    return hashlib.md5(email.lower().encode()).hexdigest()

def verify_subscription(email):
    """Verify if email is subscribed to Mailchimp list.

    Status can be one of:
        - 'subscribed': Member is subscribed
        - 'unsubscribed': Member has unsubscribed
        - 'cleaned': Member was removed due to bounces
        - 'pending': Member hasn't confirmed opt-in
        - 'transactional': Member only receives transactional emails
        - 'archived': Member was archived
    """
    try:
        client = get_mailchimp_client()
        subscriber_hash = generate_email_hash(email)

        # Get member info - https://mailchimp.com/developer/marketing/api/list-members/get-member-info/
        member = client.lists.get_list_member(
            settings.MAILCHIMP_LIST_ID,
            subscriber_hash
        )
        return True, member["status"]

    except ApiClientError as e:
        error_msg = str(e)
        if "Resource Not Found" in error_msg:
            # Member not found is expected for new subscribers
            return False, None
        else:
            # Log unexpected errors
            log_message(f"Error verifying subscription for {email}: {error_msg}", "ERROR", error=e)
            return False, None