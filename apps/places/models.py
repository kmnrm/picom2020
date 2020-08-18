from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
import pinyin
from geopy.exc import GeocoderServiceError
import phonenumbers
from phonenumber_field.modelfields import PhoneNumberField

from izhevsk.settings import BAIDUV3_GEOCODER_KEY
from geopy.geocoders import BaiduV3


def fetch_address_coordinates(address):
    locator = BaiduV3(api_key=BAIDUV3_GEOCODER_KEY)
    location = locator.geocode(
        address,
        timeout=300
    )
    return location.longitude, location.latitude


class PlaceQuerySet(models.QuerySet):
    def calculate_average_price(self):
        places = self.annotate(
            average_price_for_drink=models.Avg('drinks__price')
        ).order_by('id')
        for place in places:
            price = place.average_price_for_drink
            place.average_price = int(price) if price else 0
        return places


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
    title = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos/', default='', blank=True)
    category = models.CharField(max_length=1, choices=CATEGORIES, default='O', blank=True, null=True)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=200)
    pinyin_address = models.CharField(max_length=200, blank=True, null=True)
    opening_hours = models.TimeField(blank=True, null=True)
    closing_hours = models.TimeField(blank=True, null=True)
    average_price = models.FloatField(
        default=0,
        blank=True,
        null=True,
    )
    police_rating = models.CharField(max_length=3, choices=POLICE_RATING, default='PS1', blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, db_index=True)
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
    likes = models.ManyToManyField(User, related_name="liked_places", blank=True)
    dislikes = models.ManyToManyField(User, related_name="disliked_places", blank=True)
    objects = PlaceQuerySet.as_manager()

    def logo_url(self):
        if self.logo and hasattr(self.logo, 'url'):
            return self.logo.url
        else:
            return '/static/img/no_logo.jpg'

    def standardize_phone_number(self):
        empty_phone = ''
        if self.phone_number == empty_phone:
            return '-'
        return phonenumbers.format_number(
            self.phone_number,
            phonenumbers.PhoneNumberFormat.NATIONAL
        )

    def __str__(self):
        return f"{self.title}"


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


class PlaceImage(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')
    order_number = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.order_number} {self.place.title}"

    class Meta:
        ordering = ['order_number']


class Event(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=100)
    description = models.TextField('Краткое описание', blank=True)
    image = models.ImageField(upload_to='events/', blank=True)
    date = models.DateField(null=True)
    time_from = models.TimeField(blank=True, null=True)
    time_till = models.TimeField(blank=True, null=True)
    fee = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        default=0,
    )

    def __str__(self):
        return f"{self.title} {self.date} ({self.time_from} - {self.time_till})"


class PlaceUserReview(models.Model):
    RATING_CHOICES = (
        (0, 'Not rated'),
        (1, 'Poor'),
        (2, 'Average'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent')
    )
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=0)
    text = models.TextField("Текст комментария")
    published_at = models.DateTimeField(auto_now_add=True, blank=True)

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
    title = models.CharField(max_length=100, db_index=True)
    price = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        default=0,
    )
