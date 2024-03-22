# Generated by Django 4.2.4 on 2024-01-01 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_app', '0014_remove_rental_is_rental_approved_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rental',
            name='is_rental_approved',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='rental',
            name='is_rental_request',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='rental',
            name='is_return_approved',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='rental',
            name='is_return_request',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
