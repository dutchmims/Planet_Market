from django import template
from planet_market.utils import is_staff_member

register = template.Library()


@register.filter(name='debug_groups')
def debug_groups(user):
    """Debug filter to show user groups"""
    return [group.name for group in user.groups.all()]


@register.filter(name='is_staff')
def is_staff(user):
    """Template filter to check if user is staff member
    Usage in template:
    {% if request.user|is_staff %}
        <!-- Staff content -->
    {% endif %}
    """
    return is_staff_member(user)


@register.inclusion_tag('includes/staff_block.html')
def staff_block(user):
    """Inclusion tag that renders staff-specific content
    Usage in template:
    {% staff_block request.user %}
    """
    return {
        'is_staff': is_staff_member(user)
    }
