# Generated by Django 3.1 on 2020-08-22 14:58

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0020_auto_20200820_1241'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='place',
            options={'ordering': ['title']},
        ),
        migrations.AlterField(
            model_name='drink',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Price in CNY from CNY0 to CNY9999.99', max_digits=6),
        ),
        migrations.AlterField(
            model_name='drink',
            name='title',
            field=models.CharField(db_index=True, help_text='The drink title, as it is in a place bar card.', max_length=100),
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(blank=True, help_text='Event description.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='fee',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Entrance fee.', max_digits=6),
        ),
        migrations.AlterField(
            model_name='event',
            name='time_from',
            field=models.TimeField(blank=True, help_text='Time of the beginning of an event.', null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='time_till',
            field=models.TimeField(blank=True, help_text='Time of the ending of an event.', null=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='average_price',
            field=models.FloatField(blank=True, default=0, help_text='Automatically calculated as mean of place drinks prices.', null=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='category',
            field=models.CharField(choices=[('P', 'Pub'), ('C', 'Club'), ('E', 'Eatery'), ('B', 'Bar'), ('O', 'Others')], default='O', help_text='Place category. May be one of five: Pub, Club, Eatery, Bar, or Others (by default).', max_length=1),
        ),
        migrations.AlterField(
            model_name='place',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, db_index=True, help_text='Place contact number presented in national CN format.', max_length=128, region=None),
        ),
        migrations.AlterField(
            model_name='place',
            name='pinyin_address',
            field=models.CharField(blank=True, help_text='Automatically set field. Is a pinyin representation of place address in Chinese.', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='police_rating',
            field=models.CharField(blank=True, choices=[('PS1', '1 - No cases yet'), ('PS2', '2 - Better be cautious'), ('PS3', '3 - Periodically monitored'), ('PS4', '4 - Constantly monitored'), ('PS5', '5 - Detention cases')], default='PS1', help_text='May have value from 1 (safe) to 5 (totally unsafe).', max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='rating',
            field=models.FloatField(default=0.0, help_text='Automatically calculated as mean of users rates given to a place.'),
        ),
        migrations.AlterField(
            model_name='place',
            name='title',
            field=models.CharField(help_text='Place title.', max_length=100),
        ),
        migrations.AlterField(
            model_name='placeuserreview',
            name='published_at',
            field=models.DateTimeField(auto_now_add=True, help_text='Set automatically as the current time by the time of a POST request.'),
        ),
        migrations.AlterField(
            model_name='placeuserreview',
            name='rating',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Not rated'), (1, 'Poor'), (2, 'Average'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], default=0, help_text='Rate from 1 (Poor) to 5 (Excellent) set by a user (review author).\nTakes 0 (not rated), if the author has not rated the place.'),
        ),
        migrations.AlterField(
            model_name='placeuserreview',
            name='text',
            field=models.TextField(help_text='Review content.'),
        ),
    ]
