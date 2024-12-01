import uuid
from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django_countries.fields import CountryField
from products.models import Product
from profiles.models import UserProfile
from django.utils import timezone


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)
    user_profile = models.ForeignKey(
        UserProfile, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True, 
        related_name='orders'
    )
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = CountryField(blank_label='Country *', null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(
        max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0)
    original_bag = models.TextField(null=False, blank=False, default='')
    stripe_pid = models.CharField(
        max_length=254, null=False, blank=False, default='')
    discount_code = models.ForeignKey(
        'DiscountCode', on_delete=models.SET_NULL, null=True, blank=True)

    def _generate_order_number(self):
        """Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """Update grand total each time a line item is added,
        accounting for delivery costs and discounts.
        """
        self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))[
            'lineitem_total__sum'] or 0

        # Apply discount if a discount code is applied
        if self.discount_code:
            self.grand_total = self.order_total - \
                ((self.discount_code.discount_percentage / 100)
                 * self.order_total) + self.delivery_cost
        else:
            self.grand_total = self.order_total + self.delivery_cost

        # Check if eligible for free delivery
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.order_total * \
                settings.STANDARD_DELIVERY_PERCENTAGE / 100
        else:
            self.delivery_cost = 0

        self.save()

    def save(self, *args, **kwargs):
        """Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def apply_discount_code(self, code):
        """Apply a discount code to the order.
        """
        try:
            discount_code = DiscountCode.objects.get(
                code=code, active=True, expiry_date__gt=timezone.now())
            self.discount_code = discount_code
            self.update_total()
            return True, "Discount applied successfully."
        except DiscountCode.DoesNotExist:
            return False, "Invalid discount code or expired."

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    order = models.ForeignKey(
        Order,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='lineitems'
    )
    product = models.ForeignKey(
        Product, null=False, blank=False, on_delete=models.CASCADE)
    product_size = models.CharField(
        max_length=2, null=True, blank=True)  # XS, S, M, L, XL
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=False,
        blank=False,
        editable=False
    )

    def save(self, *args, **kwargs):
        """Override the original save method to set the lineitem total
        and update the order total.
        """
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)
        # Update the order total after saving the line item
        self.order.update_total()

    def __str__(self):
        return f'SKU {self.product.sku} on order {self.order.order_number}'


class DiscountCode(models.Model):
    code = models.CharField(max_length=15, unique=True,
                            null=False, blank=False,
                            help_text="Enter a unique discount code")

    discount_percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text="Enter discount percentage (0-100)"
    )
    active = models.BooleanField(
        default=True,
        help_text="Toggle to enable/disable this discount code"
    )

    expiry_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.code)
