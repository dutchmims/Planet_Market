from django import forms
from django.core.validators import RegexValidator
from .models import Order, DiscountCode
from django_countries.fields import CountryField
import re
from django.contrib import messages

# Define validators with messages
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,17}$',
    message=(
        "Please enter a valid phone number "
        "(e.g., +44123456789 or 07123456789)"
    )
)

# Combined regex for UK, Ireland, and US postcodes
postal_code_regex = RegexValidator(
    regex=(
        r'^(([A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2})|'
        r'([A-Z]{1,2}[0-9]{1,2})|'
        r'([0-9]{5}(-[0-9]{4})?)|'
        r'([A-Z][0-9]{2}\s[A-Z0-9]{4}))$'
    ),
    message=(
        "Please enter a valid postal code:\n"
        "• UK: e.g., SW1A 1AA or M1 1AA\n"
        "• Ireland (Eircode): e.g., D02 AF30 (must include space)\n"
        "• US: e.g., 90210 or 90210-1234"
    )
)


class OrderForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=50,
        required=True,
        error_messages={
            'required': 'Please enter your full name',
            'max_length': 'Name cannot exceed 50 characters'
        }
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        error_messages={
            'required': 'Please enter your email address',
            'invalid': 'Please enter a valid email address'
        }
    )
    phone_number = forms.CharField(
        validators=[phone_regex],
        max_length=17,
        help_text="Enter a valid international phone number",
        error_messages={
            'required': 'Phone number is required',
            'max_length': 'Phone number cannot exceed 17 characters'
        }
    )
    street_address1 = forms.CharField(
        max_length=80,
        required=True,
        error_messages={
            'required': 'Please enter your street address',
            'max_length': 'Address cannot exceed 80 characters'
        }
    )
    street_address2 = forms.CharField(
        max_length=80,
        required=False
    )
    town_or_city = forms.CharField(
        max_length=40,
        required=True,
        error_messages={
            'required': 'Please enter your town or city',
            'max_length': 'Town/city name cannot exceed 40 characters'
        }
    )
    county = forms.CharField(
        max_length=80,
        required=False
    )
    postcode = forms.CharField(
        validators=[postal_code_regex],
        max_length=20,
        help_text=(
            "Enter a postal code in one of these formats:\n"
            "• UK: SW1A 1AA or M1 1AA\n"
            "• Ireland (Eircode): D02 AF30 (must include space)\n"
            "• US: 90210 or 90210-1234"
        ),
        error_messages={
            'required': 'Postal code is required',
            'max_length': 'Postal code cannot exceed 20 characters',
            'invalid': (
                "Invalid postal code format. Please use:\n"
                "• UK: SW1A 1AA or M1 1AA\n"
                "• Ireland (Eircode): D02 AF30 (must include space)\n"
                "• US: 90210 or 90210-1234"
            )
        }
    )
    country = CountryField(blank_label='Country *').formfield(
        required=True,
        error_messages={
            'required': 'Please select your country'
        }
    )
    discount_code = forms.CharField(
        required=False,
        max_length=15,
        error_messages={
            'max_length': 'Discounts code cannot exceed 15 characters'
        }
    )

    class Meta:
        model = Order
        fields = (
            'full_name', 'email', 'phone_number',
            'street_address1', 'street_address2',
            'town_or_city', 'county', 'postcode',
            'country', 'discount_code'
        )

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        # Remove any spaces or hyphens
        phone = ''.join(filter(str.isdigit, phone))
        if len(phone) < 10:
            raise forms.ValidationError(
                "Please enter a valid phone number with at least 9 digits",
                code='invalid_phone'
            )
        return phone

    def clean_postcode(self):
        postal_code = self.cleaned_data.get('postcode', '').upper()
        if not postal_code:
            return postal_code

        # Additional validation to provide more specific error messages
        uk_pattern = r'^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$'
        # Eircode format:
        # Letter + 2 digits + space + 4 alphanumeric
        ireland_pattern = r'^[A-Z][0-9]{2}\s[A-Z0-9]{4}$'
        us_pattern = r'^[0-9]{5}(-[0-9]{4})?$'

        if not (re.match(uk_pattern, postal_code) or
                re.match(ireland_pattern, postal_code) or
                re.match(us_pattern, postal_code)):
            raise forms.ValidationError(
                "Invalid postal code. Please use one of these formats:\n"
                "• UK: SW1A 1AA or M1 1AA\n"
                "• Ireland (Eircode): D02 AF30 (must include space)\n"
                "• US: 90210 or 90210-1234",
                code='invalid_postal'
            )
        return postal_code

    def clean_discount_code(self):
        code = self.cleaned_data.get('discount_code')
        if not code:  # If no code provided, that's fine
            return code

        code = code.strip().upper()  # Normalize the code
        try:
            discount = DiscountCode.objects.get(code=code)
            if not discount.active:
                messages.error(
                    self.request,
                    'This discount code has expired'
                )
                raise forms.ValidationError(
                    'This discount code has expired'
                ) from None
            return code
        except DiscountCode.DoesNotExist as err:
            messages.error(
                self.request,
                'This discount code is invalid. Try again'
            )
            raise forms.ValidationError(
                'Invalid discount code. Please check and try again'
            ) from err

    def __init__(self, *args, **kwargs):
        """Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County, State or Locality',
            'discount_code': 'Discount Code (Optional)'
        }

        self.fields['full_name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if field != 'country':
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False


class DiscountCodeForm(forms.ModelForm):
    class Meta:
        model = DiscountCode
        fields = ['code']