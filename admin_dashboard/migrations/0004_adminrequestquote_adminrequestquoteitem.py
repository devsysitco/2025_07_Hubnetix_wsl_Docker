# Generated by Django 5.1.4 on 2025-05-09 09:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_dashboard', '0003_thelist_listitem'),
        ('catalog', '0008_category_seo_name_product_seo_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminRequestQuote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_username', models.CharField(blank=True, max_length=150)),
                ('list_name', models.CharField(max_length=255)),
                ('list_note', models.TextField(blank=True, null=True)),
                ('total_items', models.PositiveIntegerField(default=0)),
                ('request_date', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('COMPLETED', 'Completed')], default='PENDING', max_length=20)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admin_quote_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Admin Quote Request',
                'verbose_name_plural': 'Admin Quote Requests',
                'ordering': ['-request_date'],
            },
        ),
        migrations.CreateModel(
            name='AdminRequestQuoteItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=255)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admin_quote_request_items', to='catalog.product')),
                ('quote_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='admin_dashboard.adminrequestquote')),
            ],
            options={
                'verbose_name': 'Admin Quote Request Item',
                'verbose_name_plural': 'Admin Quote Request Items',
            },
        ),
    ]
