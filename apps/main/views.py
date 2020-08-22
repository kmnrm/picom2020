from json import loads, dumps
from django.urls import reverse
from rest_framework import renderers
from rest_framework.response import Response

from apps.places.views import PlaceViewSet


def to_dict(input_ordered_dict):
    return loads(dumps(input_ordered_dict))


def format_time(time_str):
    if time_str is None:
        return ""
    return time_str[:-3]


def make_feature_for_geojson(place):
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [place.longitude, place.latitude],
        },
        "properties": {
            "title": place.title,
            "placeId": place.pk,
            "detailsUrl": reverse('places-detail', args=[place.pk]),
        }
    }
    return feature


def get_rating_status(rating):
    rating_range = {
        0: 'Not rated',
        1: 'Poor',
        2: 'Average',
        3: 'Good',
        4: 'Very Good',
        5: 'Excellent'
    }
    return rating_range[round(rating)]


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
        serializer = self.get_serializer(queryset, many=True)

        places_geojson = {
            "type": "FeatureCollection",
            "features": [],
        }

        top_places = sorted(
            serializer.data,
            key=lambda k: k['rating'],
            reverse=True
        )[:4]

        top_places = [to_dict(place) for place in top_places]

        for place in top_places:
            place["police_rating"] = place["police_rating"][0]
            place["police_rating_status"] = place["police_rating"][4:]
            place["opening_hours"] = format_time(place["opening_hours"])
            place["closing_hours"] = format_time(place["closing_hours"])
            place["rating_status"] = get_rating_status(place["rating"])

        for place in queryset:
            feature = make_feature_for_geojson(place)
            places_geojson["features"].append(feature)

        return Response({
            "places_geojson": places_geojson,
            "top_places": top_places
        })
