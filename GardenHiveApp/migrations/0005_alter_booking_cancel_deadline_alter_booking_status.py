# Generated by Django 4.1.7 on 2025-03-25 05:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GardenHiveApp', '0004_rename_added_at_staff_date_joined_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='cancel_deadline',
            field=models.DateTimeField(default=datetime.datetime(2025, 4, 4, 5, 57, 21, 618255, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
    ]
