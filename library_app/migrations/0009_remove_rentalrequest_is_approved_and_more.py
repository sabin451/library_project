# Generated by Django 4.2.4 on 2023-12-28 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_app', '0008_rentalrequest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rentalrequest',
            name='is_approved',
        ),
        migrations.AddField(
            model_name='rentalrequest',
            name='is_rental_approved',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='rentalrequest',
            name='is_return_approved',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='rentalrequest',
            name='is_rental_request',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AlterField(
            model_name='rentalrequest',
            name='is_return_request',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='rentalrequest',
            name='request_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
