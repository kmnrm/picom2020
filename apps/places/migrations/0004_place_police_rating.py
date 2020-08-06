# Generated by Django 3.1 on 2020-08-04 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0003_auto_20200804_1900'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='police_rating',
            field=models.CharField(choices=[('PS1', 'No cases yet'), ('PS2', 'Better be cautious'), ('PS3', 'Periodically monitored'), ('PS4', 'Constantly monitored'), ('PS5', 'Detention cases')], default='PS1', max_length=3),
        ),
    ]
