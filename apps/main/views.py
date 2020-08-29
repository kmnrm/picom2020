import random

from django.urls import reverse
from rest_framework import renderers
from rest_framework.response import Response

from apps.places.views import PlaceViewSet
from apps.places.models import get_rating_status


def make_feature_for_geojson(place):
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [
                place.longitude,
                place.latitude
            ],
        },
        "properties": {
            "title": place.title,
            "placeId": place.id,
            "category": place.get_category_display(),
            "logo": place.logo_url(),
            "rating": place.rating,
            "ratingStatus": get_rating_status(place.rating),
            "policeRating": int(place.get_police_rating_display()[0]),
            "policeRatingStatus": place.get_police_rating_display()[4:],
            "address": place.address,
            "openingHours": place.opening_hours,
            "closingHours": place.closing_hours,
            "detailsUrl": reverse('places-detail', args=[place.pk]),
            "phoneNumber": place.standardize_phone_number(),
            "randomImage": random.choice(
                [image.image.url for image in place.images.all()]
            ) if len(place.images.all()) else ''
        }
    }
    return feature


class MainViewSet(PlaceViewSet):
    swagger_schema = None
    renderer_classes = [
        renderers.TemplateHTMLRenderer
    ]
    template_name = 'index.html'
    pagination_class = None
    filter_backends = []

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        places_geojson = {
            "type": "FeatureCollection",
            "features": [],
        }

        for place in queryset:
            feature = make_feature_for_geojson(place)
            places_geojson["features"].append(feature)

        return Response({
            "places_geojson": places_geojson,
        })
