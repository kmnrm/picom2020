from django.urls import reverse

from rest_framework import renderers
from rest_framework.response import Response

from apps.places.views import PlaceViewSet


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


class MainViewSet(PlaceViewSet):
    renderer_classes = [
        renderers.TemplateHTMLRenderer
    ]
    template_name = 'index.html'
    pagination_class = None

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
        )[:3]

        for place in top_places:
            place['police_rating'] = int(place['police_rating'][0])

        for order_in_queryset, place in enumerate(queryset):
            feature = make_feature_for_geojson(place)
            places_geojson["features"].append(feature)

        return Response({
            "places_geojson": places_geojson,
            "top_places": top_places,
        })
