# Generated by Django 3.1 on 2020-08-30 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0028_auto_20200830_1637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='placeuserreview',
            name='is_visible',
            field=models.BooleanField(default=False),
        ),
    ]
