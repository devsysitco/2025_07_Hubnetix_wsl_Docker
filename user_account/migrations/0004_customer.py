# Generated by Django 5.1.4 on 2025-05-05 11:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_account', '0003_partner'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('customer_type', models.CharField(choices=[('REGULAR', 'Regular Customer'), ('PREMIUM', 'Premium Customer'), ('VIP', 'VIP Customer')], default='REGULAR', help_text='Designates the type of customer', max_length=50)),
                ('date_of_birth', models.DateField(blank=True, help_text='Date of birth of the customer', null=True)),
                ('address', models.TextField(blank=True, help_text='Customer address', max_length=500, verbose_name='address')),
                ('loyalty_points', models.PositiveIntegerField(default=0, help_text='Points accumulated by the customer')),
                ('preferred_contact_method', models.CharField(choices=[('EMAIL', 'Email'), ('PHONE', 'Phone'), ('TEXT', 'Text Message')], default='EMAIL', help_text='Preferred method of contact', max_length=20)),
                ('customer_since', models.DateField(auto_now_add=True, help_text='Date when the customer account was created')),
            ],
            options={
                'verbose_name': 'Customer',
                'verbose_name_plural': 'Customers',
            },
            bases=('user_account.user',),
        ),
    ]
