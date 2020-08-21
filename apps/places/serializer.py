from rest_framework import serializers
from apps.places.models import (Place,
                                PlaceImage,
                                Event,
                                PlaceUserReview,
                                Drink)


def format_time(time):
    time_hh_mm = str(time)[:-3]
    return time_hh_mm[1:] if time_hh_mm.startswith('0') \
        else time_hh_mm


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

    def get_username(self, review):
        return review.author.username


class PlaceSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.PrimaryKeyRelatedField(read_only=True)
    coordinates = serializers.SerializerMethodField()
    events = EventSerializer(many=True, read_only=True)
    images = serializers.SerializerMethodField()
    police_rating = serializers.ChoiceField(choices=Place.POLICE_RATING)
    average_price = serializers.SerializerMethodField()
    pinyin_address = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True)
    logo = serializers.SerializerMethodField('get_logo_url')
    phone_number = serializers.SerializerMethodField()
    similar_places = serializers.SerializerMethodField(read_only=True)
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
            'reviews',
            'similar_places',
            'detailsUrl',
        )

    def create(self, validated_data):
        validated_data.update(
            {
                'uploaded_by': self.context['request'].user,
                'average_price': 0,
            }
        )
        place = Place.objects.create(**validated_data)
        return place

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
        ret['category'] = [
            value
            for key, value in Place.CATEGORIES
            if key == ret['category']
        ][0]
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

    def get_similar_places(self, place):
        similar_places = Place.objects.filter(category=place.category).exclude(id=place.id)
        return [
            RelatedPlaceSerializer(similar_place, context=self.context).data
            for similar_place in similar_places
        ]


class RelatedPlaceSerializer(PlaceSerializer):
    detailsUrl = serializers.HyperlinkedIdentityField(view_name="places-detail", lookup_field='pk')

    class Meta:
        model = Place
        fields = (
            'id',
            'title',
            'rating',
            'police_rating',
            'category',
            'logo',
            'coordinates',
            'detailsUrl',
        )


class DrinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drink
        fields = '__all__'
