# Generated by Django 3.1 on 2020-08-28 08:29

import apps.places.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0025_auto_20200828_0124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='placeimage',
            name='image',
            field=models.ImageField(upload_to=apps.places.models.set_upload_location),
        ),
    ]
