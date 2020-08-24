# Generated by Django 3.1 on 2020-08-24 13:55

from django.db import migrations
import stdimage.models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0023_remove_place_similar_places'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='logo',
            field=stdimage.models.StdImageField(blank=True, default='', upload_to='logos/'),
        ),
    ]