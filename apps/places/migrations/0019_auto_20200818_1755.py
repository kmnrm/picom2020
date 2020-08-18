# Generated by Django 3.1 on 2020-08-18 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0018_place_phone_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='datetime',
        ),
        migrations.AddField(
            model_name='event',
            name='date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='time_from',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='time_till',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
