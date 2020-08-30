# Generated by Django 3.1 on 2020-08-30 19:32
import random
import datetime

from django.db import migrations


def add_events(apps, schema_editor):
    Event = apps.get_model('places', 'Event')
    dates = [
        datetime.date(2020, month, day)
        for day in range(1, 28)
        for month in range(9, 13)
    ]
    for event in Event.objects.all():
        event.date = random.choice(dates)
        event.save()


def remove_events(apps, schema_editor):
    Event = apps.get_model('places', 'Event')
    Event.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0030_auto_20200830_2249'),
    ]

    operations = [
        migrations.RunPython(
            add_events,
            remove_events
        )
    ]
