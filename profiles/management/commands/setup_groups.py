from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = 'Creates default groups and permissions'

    def handle(self, *args, **options):
        # Create Public group (for anonymous users)
        public_group, created = Group.objects.get_or_create(name='Public')
        if created:
            self.stdout.write(self.style.SUCCESS(
                'Created Public group'))

        # Create Customer group
        customer_group, created = Group.objects.get_or_create(name='Customer')
        if created:
            self.stdout.write(self.style.SUCCESS(
                'Created Customer group'))

        # Create Staff group
        staff_group, created = Group.objects.get_or_create(
            name='Staff')
        if created:
            self.stdout.write(self.style.SUCCESS(
                'Created Staff group'))

        # Set up public permissions (anonymous users)
        public_permissions = [
            'view_product',     # Can view products
            'add_order',        # Can create orders
            'view_order',       # Can view their current order
        ]

        # Get and assign permissions to public group
        for perm_codename in public_permissions:
            try:
                perm = Permission.objects.get(
                    codename=perm_codename)
                public_group.permissions.add(perm)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'Permission {perm_codename} not found'))

        # Customer permissions (registered users)
        customer_permissions = [
            'view_product',     # Can view products
            'view_order',       # Can view order history
            'add_order',        # Can create orders
            'view_userprofile',  # Can view their profile
            'change_userprofile',  # Can update their profile
        ]

        # Get and assign permissions to customer group
        for perm_codename in customer_permissions:
            try:
                perm = Permission.objects.get(
                    codename=perm_codename)
                customer_group.permissions.add(perm)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'Permission {perm_codename} not found'))

        # Staff permissions (most privileged)
        staff_permissions = [
            'view_product', 'add_product', 'change_product', 'delete_product',
            'view_order', 'change_order', 'delete_order',
            'view_userprofile', 'change_userprofile', 'delete_userprofile'
        ]

        # Get and assign permissions to staff group
        for perm_codename in staff_permissions:
            try:
                perm = Permission.objects.get(
                    codename=perm_codename)
                staff_group.permissions.add(perm)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'Permission {perm_codename} not found'))

        self.stdout.write(self.style.SUCCESS(
            'Successfully set up groups and permissions'))
