# Generated by Django 3.1 on 2020-08-30 20:25
import random
from django.db import migrations


def add_reviews(apps, schema_editor):
    Review = apps.get_model('places', 'PlaceUserReview')
    Place = apps.get_model('places', 'Place')

    with open('random_sentences2.txt', 'r') as f:
        review_texts = [line.strip() for line in f.readlines()]

    for text in review_texts:
        reviewed_place = random.choice([place for place in Place.objects.all()])
        rating = random.randint(1, 5)
        Review.objects.get_or_create(
            place=reviewed_place,
            rating=rating,
            text=text,
            is_visible=True,
        )


def remove_reviews(apps, schema_editor):
    Review = apps.get_model('places', 'PlaceUserReview')
    Review.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0032_auto_20200831_0013'),
    ]

    operations = [
        migrations.RunPython(
            add_reviews,
            remove_reviews
        )
    ]
