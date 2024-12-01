""" """
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """."""

    priority = 0.5
    changefreq = "daily"

    def items(self):
        """Items"""
        return ["home", "products", "profile", "subscribe"]

    def location(self, item):
        """Location"""
        return reverse(item)

