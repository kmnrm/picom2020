# Generated by Django 3.1 on 2020-08-23 16:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0022_place_similar_places'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='place',
            name='similar_places',
        ),
    ]
