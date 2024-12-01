from django.contrib.auth.decorators import (
    user_passes_test)


def is_staff_member(user):
    """Check if user is authenticated and
    belongs to Staff group
    """

    return user.is_authenticated and \
        user.groups.filter(
            name='Staff').exists()


def staff_member_required(view_func):
    """A decorator for views that checks
    if the user is a staff member.
    """

    return user_passes_test(
        is_staff_member,
        login_url='account_login',
        redirect_field_name='next'
    )(view_func)

