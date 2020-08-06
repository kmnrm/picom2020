from rest_framework import serializers
from apps.places.models import (Place,
                                PlaceImage,
                                Event,
                                PlaceUserReview,
                                Drink)

from izhevsk.settings import BAIDUV3_GEOCODER_KEY
from collections import Counter
from geopy.geocoders import BaiduV3


def fetch_address_coordinates(serializer_create_validated_data):
    locator = BaiduV3(api_key=BAIDUV3_GEOCODER_KEY)
    location = locator.geocode(
        serializer_create_validated_data['address'],
        timeout=300
    )
    return location.longitude, location.latitude


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class PlaceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceImage
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = PlaceUserReview
        fields = '__all__'

    def create(self, validated_data):
        validated_data.update(
            {
                'author': self.context['request'].user,
            }
        )
        review = PlaceUserReview.objects.create(**validated_data)
        return review


class PlaceSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.PrimaryKeyRelatedField(read_only=True)
    coordinates = serializers.SerializerMethodField()
    events = EventSerializer(many=True, read_only=True)
    images = PlaceImageSerializer(many=True, read_only=True)
    police_rating = serializers.ChoiceField(choices=Place.POLICE_RATING)
    rating = serializers.SerializerMethodField()
    average_price = serializers.SerializerMethodField()
    pinyin_address = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Place
        fields = (
            'id',
            'uploaded_by',
            'title',
            'address',
            'pinyin_address',
            'description',
            'average_price',
            'police_rating',
            'opening_hours',
            'closing_hours',
            'coordinates',
            'events',
            'images',
            'rating',
            'reviews',
        )

    def create(self, validated_data):
        lon, lat = fetch_address_coordinates(validated_data)
        validated_data.update(
            {
                'uploaded_by': self.context['request'].user,
                'longitude': lon,
                'latitude': lat,
                'average_price': 0,
            }
        )
        place = Place.objects.create(**validated_data)
        return place

    def update(self, instance, validated_data):
        lon, lat = fetch_address_coordinates(validated_data)
        validated_data.update(
            {
                'longitude': lon,
                'latitude': lat,
            }
        )
        return super(PlaceSerializer, self).update(instance, validated_data)

    def get_coordinates(self, place):
        return {
            'longitude': place.longitude,
            'latitude': place.latitude,
        }

    def to_representation(self, place):
        ret = super().to_representation(place)
        ret['police_rating'] = [
            value
            for key, value in Place.POLICE_RATING
            if key == ret['police_rating']
        ][0]
        return ret

    def get_rating(self, place):
        ratings = PlaceUserReview.objects.filter(place=place, rating__gt=0)
        ratings = Counter(ratings.values_list("rating", flat=True))
        total_ratings = sum(ratings.values())
        mean_rating = sum(
            rate * count
            for rate, count in ratings.items()
        ) / total_ratings if total_ratings > 0 else None
        return mean_rating

    def get_average_price(self, place):
        return place.average_price

    def get_pinyin_address(self, place):
        return place.pinyin_address


class DrinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drink
        fields = '__all__'
