from django.contrib import admin
from .models import Product, Category, Review, ProductVariant

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

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )

class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'user_name',
        'rating',
        'created_at',
    )
    search_fields = ('user_name', 'review_text')
    list_filter = ('rating', 'created_at')

class ProductVariantInline(admin.TabularInline):
    """Inline admin interface for product variants."""
    model = ProductVariant
    extra = 1

class ProductAdminWithVariants(admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'image',
    )
    ordering = ('sku',)
    inlines = [ProductVariantInline]

# Register your models with the appropriate admin classes
admin.site.register(Product, ProductAdminWithVariants)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Review, ReviewAdmin)
