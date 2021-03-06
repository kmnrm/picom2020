# Generated by Django 3.1 on 2020-08-05 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0011_place_pinyin_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='pinyin_address',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='police_rating',
            field=models.CharField(blank=True, choices=[('PS1', '1 - No cases yet'), ('PS2', '2 - Better be cautious'), ('PS3', '3 - Periodically monitored'), ('PS4', '4 - Constantly monitored'), ('PS5', '5 - Detention cases')], default='PS1', max_length=3),
        ),
    ]
