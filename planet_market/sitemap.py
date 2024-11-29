""" """

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from products.models import Product

class StaticViewSitemap(Sitemap):
    """Sitemap for static pages."""
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return ["home", "products", "profile"]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    """Product sitemap configuration."""
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.last_modified
