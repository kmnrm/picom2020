# Generated by Django 3.1 on 2020-08-20 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0019_auto_20200818_1755'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='place',
            name='dislikes',
        ),
        migrations.RemoveField(
            model_name='place',
            name='likes',
        ),
        migrations.AddField(
            model_name='place',
            name='rating',
            field=models.FloatField(default=0),
        ),
    ]
