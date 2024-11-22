"""boutique_ado URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# URLS
from blog.models import Post
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

# Site Maps
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import index, sitemap
from django.urls import include, path

from .sitemap import StaticViewSitemap, BlogSitemap

# Register all sitemaps
sitemaps = {
    "static": StaticViewSitemap(),
    "blog": BlogSitemap(),
}

urlpatterns = [
    # Sitemap index
    path('sitemap.xml', index, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.index'),
    # Individual sitemaps
    path('sitemap-<section>.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("home.urls")),
    path("products/", include("products.urls")),
    path("bag/", include("bag.urls")),
    path("checkout/", include("checkout.urls")),
    path("profile/", include("profiles.urls")),
    path("blog/", include("blog.urls")),
    # path("newsletter/", include("newsletter.urls")),  # x fix
]
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
else:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

handler404 = "home.views.custom_page_not_found_view"
