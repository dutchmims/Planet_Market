""" """

from blog.models import Post
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from products.models import Category, Product


class StaticViewSitemap(Sitemap):
    """."""

    priority = 0.5
    changefreq = "daily"

    def items(self):
        return ["home", "products"]

    def location(self, item):
        return reverse(item)


class BlogSitemap(Sitemap):
    """Blog sitemap configuration."""

    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Post.objects.all().order_by("-created_at")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('post_detail', args=[obj.slug])
