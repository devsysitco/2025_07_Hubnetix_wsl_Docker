# Generated by Django 5.1.4 on 2025-05-14 09:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0010_datasheet'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datasheet',
            options={'ordering': ['created_at']},
        ),
    ]
