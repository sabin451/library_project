# Generated by Django 4.1.2 on 2024-03-22 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library_app', '0015_rental_is_rental_approved_rental_is_rental_request_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='RentalRequest',
        ),
    ]
