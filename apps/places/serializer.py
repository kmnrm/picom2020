from django.contrib.auth.models import User
from rest_framework import serializers
from drf_yasg import openapi
from apps.places.models import get_rating_status
from apps.places.models import (Place,
                                PlaceImage,
                                Event,
                                PlaceUserReview,
                                Drink)


def represent_choices(ret, choices_field_name, choices):
    return [
        value
        for key, value in choices
        if key == ret[choices_field_name]
    ][0]


def format_time(time):
    time_hh_mm = str(time)[:-3]
    return time_hh_mm[1:] if time_hh_mm.startswith('0') \
        else time_hh_mm


class CoordinatesField(serializers.SerializerMethodField):
    class Meta:
        swagger_schema_fields = {
            "type": openapi.TYPE_OBJECT,
            "properties": {
                "longitude": openapi.Schema(
                    title="Address longitude coordinate. Set automatically via Baidu API.",
                    type=openapi.TYPE_NUMBER,
                ),
                "latitude": openapi.Schema(
                    title="Address latitude coordinate. Set automatically via Baidu API.",
                    type=openapi.TYPE_NUMBER,
                ),
            }
         }


class EventSerializer(serializers.ModelSerializer):
    time_from = serializers.SerializerMethodField()
    time_till = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    def get_time_from(self, event):
        return format_time(event.time_from)

    def get_time_till(self, event):
        return format_time(event.time_till)


class PlaceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceImage
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.SerializerMethodField()
    publishing_date = serializers.SerializerMethodField()
    publishing_time = serializers.SerializerMethodField()

    class Meta:
        model = PlaceUserReview
        exclude = ('published_at', 'is_visible', )
        extra_kwargs = {
            'is_visible': {'read_only': True},
        }

    def create(self, validated_data):
        author = self.context['request'].user \
            if self.context['request'].user.id \
            else User.objects.get(id=PlaceUserReview.DEFAULT_ANONYMOUS_USER_ID)

        validated_data.update(
            {
                'author': author,
            }
        )
        review = PlaceUserReview.objects.create(**validated_data)
        return review

    def get_username(self, review):
        return review.author.username

    def get_publishing_date(self, review):
        return str(review.published_at.date())

    def get_publishing_time(self, review):
        return format_time(
            review.published_at.time().replace(microsecond=0)
        )


class PlaceSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.PrimaryKeyRelatedField(read_only=True)
    coordinates = CoordinatesField()
    address = serializers.SerializerMethodField()
    events = EventSerializer(many=True, read_only=True)
    images = serializers.SerializerMethodField()
    police_rating = serializers.ChoiceField(choices=Place.POLICE_RATING)
    average_price = serializers.SerializerMethodField()
    pinyin_address = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True, source="show_visible_reviews")
    logo = serializers.SerializerMethodField('get_logo_url')
    phone_number = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    rating_status = serializers.SerializerMethodField()
    detailsUrl = serializers.HyperlinkedIdentityField(view_name="places-detail", lookup_field='pk')

    class Meta:
        model = Place
        fields = (
            'id',
            'uploaded_by',
            'title',
            'logo',
            'category',
            'address',
            'pinyin_address',
            'phone_number',
            'description',
            'average_price',
            'police_rating',
            'opening_hours',
            'closing_hours',
            'coordinates',
            'events',
            'images',
            'rating',
            'rating_status',
            'reviews',
            'detailsUrl',
        )

    def create(self, validated_data):
        validated_data.update(
            {
                'uploaded_by': self.context['request'].user,
            }
        )
        place = Place.objects.create(**validated_data)
        return Place.objects.filter(id=place.id).calculate_auto_fill_fields()[0]

    def get_coordinates(self, place):
        return {
            'longitude': place.longitude,
            'latitude': place.latitude,
        }

    def to_representation(self, place):
        ret = super().to_representation(place)
        ret['police_rating'] = represent_choices(ret, 'police_rating', Place.POLICE_RATING)
        ret['category'] = represent_choices(ret, 'category', Place.CATEGORIES)
        return ret

    def get_average_price(self, place):
        return place.average_price

    def get_pinyin_address(self, place):
        return place.pinyin_address

    def get_images(self, place):
        return [image.image.url for image in place.images.all()]

    def get_logo_url(self, place):
        return place.logo_url()

    def get_phone_number(self, place):
        return place.standardize_phone_number()

    def get_rating(self, place):
        return place.rating

    def get_rating_status(self, place):
        return get_rating_status(place.rating)

    def get_address(self, place):
        return place.address.replace('河南省', '').replace('郑州市', '')


class DrinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drink
        fields = '__all__'
