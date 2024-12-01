"""Product models for the store."""

from django.core.validators import (
    MinValueValidator, MaxValueValidator)
from django.db import models


class Category(models.Model):
    """Category model class."""

    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(
        max_length=254)
    friendly_name = models.CharField(
        max_length=254,
        null=True,
        blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Product(models.Model):
    """Product model class."""

    category = models.ForeignKey(
        'Category',
        null=True,
        blank=True,
        on_delete=models.SET_NULL)
    sku = models.CharField(
        max_length=254,
        null=True, blank=True)
    name = models.CharField(
        max_length=254)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(
                0.01,
                message="Price must be at least 0.01"),
            MaxValueValidator(
                999999.99,
                message="Price cannot exceed 999,999.99")
        ]
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(
                0.0,
                message="Rating cannot be negative"),
            MaxValueValidator(
                5.0,
                message="Rating cannot exceed 5.0")
        ]
    )
    image_url = models.URLField(
        max_length=1024,
        null=True,
        blank=True)
    image = models.ImageField(
        upload_to='product_images/',
        null=True,
        blank=True,
        default='noimage.png')

    def __str__(self):
        return self.name

    @property
    def safe_image_url(self):
        """Return a safe image URL with
        fallback to default"""
        if self.image:
            try:
                # Check if file exists
                if self.image.storage.exists(
                    self.image.name):
                    return self.image.url
            except (AttributeError,
                    ValueError,
                    Exception):
                return '/media/noimage.png'

        if self.image_url:
            return self.image_url

        return '/media/noimage.png'


class Review(models.Model):
    """Review model class."""

    product = models.ForeignKey(
        Product,
        related_name='reviews',
        on_delete=models.CASCADE)
    user_name = models.CharField(max_length=254)
    review_text = models.TextField()
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[
            MinValueValidator(
                1.0,
                message="Rating must be at least 1.0"),
            MaxValueValidator(
                5.0,
                message="Rating cannot exceed 5.0")
        ]
    )
    created_at = models.DateTimeField(
        auto_now_add=True)
    updated_at = models.DateTimeField(
        auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Review by {self.user_name}'


class ProductVariant(models.Model):
    """Product variant model class."""

    product = models.ForeignKey(
        Product,
        related_name='variants',
        on_delete=models.CASCADE)
    sku = models.CharField(max_length=254)
    size = models.CharField(max_length=50)
    color = models.CharField(max_length=50)

    def __str__(self):
        return f'''{self.product.name} -
                {self.size} {self.color}
                '''
