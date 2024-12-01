"""Newsletter forms."""

from django import forms
from .models import Subscriber


class NewsletterForm(forms.ModelForm):
    """Newsletter subscription form."""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email',
                'aria-label': (
                    'Email address for newsletter'
                )
            }
        )
    )

    class Meta:
        model = Subscriber
        fields = ['email']

    def clean_email(self):
        """Clean and normalize the email field."""
        email = self.cleaned_data['email'].\
            strip().lower()
        return email
