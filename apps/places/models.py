import datetime
import random
import string

from django.db import models
from django.contrib.auth.models import User
from django.db.models.functions import Coalesce
from django.db.models.signals import pre_save
from django.dispatch import receiver

from stdimage import StdImageField
import pinyin
from geopy.exc import GeocoderServiceError
import phonenumbers
from phonenumber_field.modelfields import PhoneNumberField

from izhevsk.settings import BAIDUV3_GEOCODER_KEY, BAIDU_SECURITY_KEY
from geopy.geocoders import BaiduV3


def get_rating_status(rating):
    rating_range = PlaceUserReview.RATING_CHOICES
    return rating_range[round(rating)][1]


def fetch_address_coordinates(address):
    locator = BaiduV3(api_key=BAIDUV3_GEOCODER_KEY, security_key=BAIDU_SECURITY_KEY)
    location = locator.geocode(
        address,
        timeout=300
    )
    return location.longitude, location.latitude


def generate_random_string(length):
    return ''.join(
        [
            random.choice(
                ''.join([string.ascii_letters, string.digits])
            )
            for i in range(length)
        ]
    )


def set_upload_location(instance, filename):
    filebase, extension = filename.split('.')
    return 'images/place%s/%s.%s' % (instance.place.id, generate_random_string(30), extension)


class Round(models.Func):
    function = 'ROUND'
    template='%(function)s(%(expressions)s, 1)'


class PlaceQuerySet(models.QuerySet):
    def calculate_auto_fill_fields(self):
        return self.annotate(
            rating=Coalesce(
                Round(
                    models.Avg(
                        'reviews__rating',
                        filter=models.Q(
                            reviews__rating__gt=0,
                            reviews__is_visible=True
                        )
                    )
                ),
                0.0
            )
        ).annotate(
            average_price=Coalesce(
                models.Avg(
                    'drinks__price',
                    output_field=models.PositiveSmallIntegerField()
                ),
                0
            )
        ).order_by('-rating')


class Place(models.Model):
    POLICE_RATING = (
        ('PS1', '1 - No cases yet'),
        ('PS2', '2 - Better be cautious'),
        ('PS3', '3 - Periodically monitored'),
        ('PS4', '4 - Constantly monitored'),
        ('PS5', '5 - Detention cases'),
    )
    CATEGORIES = (
        ('P', 'Pub'),
        ('C', 'Club'),
        ('E', 'Eatery'),
        ('B', 'Bar'),
        ('O', 'Others')
    )
    uploaded_by = models.ForeignKey(
        User,
        related_name='places',
        on_delete=models.CASCADE,
        null=True,
        db_index=True
    )
    title = models.CharField(max_length=100, help_text="Place title.")
    logo = StdImageField(
        upload_to='logos/',
        default='',
        blank=True,
        delete_orphans=True,
        variations={
            'thumbnail': {
                "width": 100,
                "height": 100,
                "crop": False
            }
        }
    )
    category = models.CharField(
        max_length=1,
        choices=CATEGORIES,
        default='O',
        help_text="Place category. May be one of five: Pub, Club, Eatery, Bar, or Others (by default).")
    description = models.TextField(blank=True)
    address = models.CharField(max_length=200)
    pinyin_address = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Automatically set field. Is a pinyin representation of place address in Chinese."
    )
    opening_hours = models.TimeField(default=datetime.time(12, 00))
    closing_hours = models.TimeField(default=datetime.time(2, 00))

    police_rating = models.CharField(
        max_length=3,
        choices=POLICE_RATING,
        default='PS1',
        blank=True,
        null=True,
        help_text="May have value from 1 (safe) to 5 (totally unsafe)."
    )
    phone_number = PhoneNumberField(
        blank=True,
        db_index=True,
        help_text="Place contact number presented in national CN format."
    )
    latitude = models.FloatField(
        blank=True,
        null=True,
        help_text="Latitude coordinate related to the address."
    )
    longitude = models.FloatField(
        blank=True,
        null=True,
        help_text="Longitude coordinate related to the address."
    )

    objects = PlaceQuerySet.as_manager()

    def logo_url(self):
        if self.logo and hasattr(self.logo, 'url'):
            return self.logo.thumbnail.url
        else:
            return '/static/img/no_logo.jpg'

    def standardize_phone_number(self):
        empty_phone = ''
        if self.phone_number == empty_phone:
            self.phone_number = phonenumbers.parse("13299999999", 'CN')
        return phonenumbers.format_number(
            self.phone_number,
            phonenumbers.PhoneNumberFormat.NATIONAL
        )

    def show_visible_reviews(self):
        return PlaceUserReview.objects.filter(place=self, is_visible=True).order_by('published_at')

    def __str__(self):
        return f"{self.title}"

    class Meta:
        ordering = ['title']


class PlaceImage(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=set_upload_location)
    order_number = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.order_number} {self.place.title}"

    class Meta:
        ordering = ['order_number']


class Event(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, help_text="Event description.")
    image = models.ImageField(upload_to='events/', blank=True)
    date = models.DateField(null=True)
    time_from = models.TimeField(
        blank=True,
        null=True,
        help_text="Time of the beginning of an event."
    )
    time_till = models.TimeField(
        blank=True,
        null=True,
        help_text="Time of the ending of an event."
    )
    fee = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        default=0,
        help_text="Entrance fee."
    )

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.title} {self.date} ({self.time_from} - {self.time_till})"


class PlaceUserReview(models.Model):
    DEFAULT_ANONYMOUS_USER_ID = 63
    RATING_CHOICES = (
        (0, 'Not rated'),
        (1, 'Poor'),
        (2, 'Average'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent')
    )
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(
        User,
        related_name='reviews',
        on_delete=models.CASCADE,
        default=DEFAULT_ANONYMOUS_USER_ID,
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        default=0,
        help_text="Rate from 1 (Poor) to 5 (Excellent) set by a user (review author).\n"
                  "Takes 0 (not rated), if the author has not rated the place."
    )
    text = models.TextField(help_text="Review content.")
    published_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        help_text="Set automatically as the current time by the time of a POST request."
    )
    is_visible = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.author.username} " \
               f"reviewed {self.place.title} " \
               f"on {self.published_at.strftime('%B %d %Y')}"

    class Meta:
        ordering = ['published_at']


class Drink(models.Model):
    place = models.ForeignKey(
        Place,
        related_name="drinks",
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        max_length=100,
        db_index=True,
        help_text="The drink title, as it is in a place bar card."
    )
    price = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        default=0,
        help_text="Price in CNY from CNY0 to CNY9999.99"
    )


@receiver(pre_save, sender=Place)
def get_pinyin_address(sender, instance, **kwargs):
    city_name_full = 'hé nán shěng zhèng zhōu shì'
    city_name_short = 'hé nán zhèng zhōu'
    pinyin_address = pinyin.get(instance.address, format='diacritical', delimiter=" ")
    if pinyin_address.startswith(city_name_full):
        instance.pinyin_address = pinyin_address.replace(city_name_full, '')
    elif pinyin_address.startswith(city_name_short):
        instance.pinyin_address = pinyin_address.replace(city_name_short, '')
    else:
        instance.pinyin_address = pinyin_address


@receiver(pre_save, sender=Place)
def geocode_address(sender, instance, **kwargs):
    try:
        instance.longitude, instance.latitude = fetch_address_coordinates(
            instance.address
        )
    except GeocoderServiceError:
        instance.longitude = instance.latitude = None
