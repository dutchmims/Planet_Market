from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from django.db import transaction


@receiver(post_save, sender=User)
def assign_customer_group(sender, instance, created, **kwargs):
    """ assign_customer_group
    Signal to automatically assign newly
    registered users to the Customer group
    """

    if created:  # only for newly created users
        try:
            with transaction.atomic():
                customer_group = Group.objects.get(name='Customer')
                instance.groups.add(customer_group)
        except Group.DoesNotExist:
            # Log this error in production
            pass
