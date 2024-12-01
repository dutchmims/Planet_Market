"""Newsletter utility functions."""

import hashlib
import json
import logging
from datetime import datetime
from django.conf import settings
from mailchimp_marketing.api_client import (
    ApiClientError)  # type: ignore
import mailchimp_marketing as MailchimpMarketing # type: ignore

# Simple logging setup for Heroku
#     Was used to try to understand 500 errors on heroku
#     Newsletter from localhost worked
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def analyze_error_source(error):
    """Get basic information about an error.
    Was used to try to understand 500 errors on heroku
    Newsletter from localhost worked
    """
    # Basic error details
    error_info = {
        'type': type(error).__name__,
        'message': str(error),
        'status_code': getattr(error, 'status_code', 'N/A')
    }

    # Add API error details if available
    if hasattr(error, 'text'):
        try:
            error_info['details'] = json.loads(error.text)
        except json.JSONDecodeError:
            error_info['details'] = error.text

    return error_info

def log_message(message, level="INFO", error=None):
    """Print a log message to console with optional
    error details.
    Was used to try to understand 500 errors on heroku
    Newsletter from localhost worked
    """
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create the log message
    log_entry = f"[{timestamp}] {level}: {message}"

    # Add error details if provided
    if error:
        error_info = analyze_error_source(error)
        log_entry += f"\nError Type: {error_info['type']}"
        log_entry += f"\nError Message: {error_info['message']}"

    # Print to console (shows in Heroku logs)
    print(log_entry, flush=True)

def get_mailchimp_client():
    """Get configured Mailchimp client with
    enhanced error handling."""
    try:
        # Verify required environment variables
        required_vars = ['MAILCHIMP_API_KEY',
                        'MAILCHIMP_REGION']
        missing_vars = [
            var for var in required_vars
            if not getattr(settings, var, None)
        ]
        if missing_vars:
            raise ValueError(
                f"""Missing required environment variables:
                {', '.join(missing_vars)}"""
            )

        client = MailchimpMarketing.Client()
        client.set_config({
            "api_key": settings.MAILCHIMP_API_KEY,
            "server": settings.MAILCHIMP_REGION
        })

        # Verify credentials with a ping
        client.ping.get()
        log_message(
            "Successfully connected to Mailchimp API",
            "INFO")
        return client

    except ApiClientError as error:
        log_message(
            "Mailchimp client configuration error",
            "ERROR",
            error
        )
        raise
    except ValueError as error:
        log_message(
            "Environment configuration error",
            "ERROR",
            error
        )
        raise
    except Exception as error:
        log_message(
            "Unexpected error in Mailchimp client setup",
            "ERROR",
            error
        )
        raise

def generate_email_hash(email):
    """Generate a hash for the email address."""
    return hashlib.md5(
        email.lower().encode()).hexdigest()