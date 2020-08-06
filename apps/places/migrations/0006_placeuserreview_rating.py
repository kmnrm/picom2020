# Generated by Django 3.1 on 2020-08-04 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0005_auto_20200804_2202'),
    ]

    operations = [
        migrations.AddField(
            model_name='placeuserreview',
            name='rating',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Poor'), (2, 'Average'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], default=1),
        ),
    ]
