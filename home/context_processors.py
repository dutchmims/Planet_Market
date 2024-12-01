from django.contrib.sites.shortcuts import get_current_site


def site_name(request):
    """Add site name to the template context.
    This allows using a dynamic site name in meta tags and templates.
    """
    site = get_current_site(request)
    return {
        'site_name': site.name,
        'site_domain': site.domain,
    }
