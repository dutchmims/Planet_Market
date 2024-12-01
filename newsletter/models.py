from django.db import models
from django.utils import timezone
from .utils import generate_email_hash


class Subscriber(models.Model):
    """Newsletter subscriber model."""
    
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': 'This email is already subscribed.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    subscribed_at = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    email_hash = models.CharField(
        max_length=32,  # MD5 hash is 32 characters
        editable=False,
        default=None,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        """Save the subscriber, converting email to lowercase and
        generating hash.
        """
        self.email = self.email.lower()
        if not self.email_hash:
            self.email_hash = generate_email_hash(self.email)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"

    class Meta:
        ordering = ['email']
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'