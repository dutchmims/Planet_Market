# Generated by Django 3.2.23 on 2024-06-30 09:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0005_discountcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='discountcode',
            name='expiry_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='discount_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='checkout.discountcode'),
        ),
    ]
