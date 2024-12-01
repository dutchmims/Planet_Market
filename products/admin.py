from django.contrib import admin
from .models import (
    Product,
    Category,
    Review,
    ProductVariant)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'image',
    )
    ordering = ('sku',)
    list_filter = ('category',)
    search_fields = ('name', 'sku')


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )
    search_fields = ('name',
                    'friendly_name')


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'user_name',
        'rating',
        'created_at',
    )
    search_fields = ('user_name',
                    'review_text')
    list_filter = ('rating',
                'created_at')


class ProductVariantInline(
    admin.TabularInline):
    # Or admin.StackedInline
    # for a different layout
    model = ProductVariant
    extra = 1
    # Number of extra forms displayed


class ProductAdminWithVariants(
    admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'image',
    )
    ordering = ('sku',)
    list_filter = ('category',)
    inlines = [ProductVariantInline]
    search_fields = ('name', 'sku')


# Register your models with
# the appropriate admin classes
admin.site.register(
    Product,
    ProductAdminWithVariants)
admin.site.register(
    Category,
    CategoryAdmin)
admin.site.register(
    Review,
    ReviewAdmin)
