# Generated by Django 4.2.4 on 2024-01-01 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_app', '0010_rental_is_rental_approved_rental_is_rental_request_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rental',
            name='is_rental_request',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
