# Generated by Django 3.1 on 2020-08-27 21:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0024_auto_20200824_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='closing_hours',
            field=models.TimeField(default=datetime.time(2, 0)),
        ),
        migrations.AlterField(
            model_name='place',
            name='opening_hours',
            field=models.TimeField(default=datetime.time(12, 0)),
        ),
    ]
