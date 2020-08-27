from json import loads, dumps

from rest_framework import renderers
from rest_framework.response import Response

from apps.places.views import PlaceViewSet
from apps.places.models import get_rating_status


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
            "coordinates": [
                place["coordinates"]["longitude"],
                place["coordinates"]["latitude"]
            ],
        },
        "properties": {
            "title": place["title"],
            "placeId": place["id"],
            "category": place["category"],
            "logo": place["logo"],
            "rating": place["rating"],
            "policeRating": int(place["police_rating"][0]),
            "address": place["address"],
            "openingHours": place["opening_hours"],
            "closingHours": place["closing_hours"],
            "detailsUrl": place["detailsUrl"],
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
        serializer = self.get_serializer(queryset, many=True)

        places_geojson = {
            "type": "FeatureCollection",
            "features": [],
        }

        places = sorted(
            serializer.data,
            key=lambda k: k['rating'],
            reverse=True
        )

        places = [to_dict(place) for place in places]

        top_places = [place.copy() for place in places[:3]]

        for place in top_places:
            place["police_rating_status"] = place["police_rating"][4:]
            place["police_rating"] = place["police_rating"][0]
            place["opening_hours"] = format_time(place["opening_hours"])
            place["closing_hours"] = format_time(place["closing_hours"])
            place["rating_status"] = get_rating_status(place["rating"])
            place["rating_rounded"] = round(place["rating"])

        for place in places:
            feature = make_feature_for_geojson(place)
            places_geojson["features"].append(feature)

        return Response({
            "places_geojson": places_geojson,
            "top_places": top_places,
        })
