from django.http import HttpResponseRedirect
from django.urls import reverse

from rest_framework import renderers
from rest_framework.response import Response

from apps.users.serializer import UserRegistrationSerializer
from apps.users.views import UserViewSet
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
    #permission_classes = [IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        places_geojson = {
            "type": "FeatureCollection",
            "features": [],
        }

        for order_in_queryset, place in enumerate(queryset):
            feature = make_feature_for_geojson(place)
            places_geojson["features"].append(feature)

        if request.accepted_renderer.format == 'html':
            return Response({
                "places_geojson": places_geojson,
                "registration_serializer": UserRegistrationSerializer
            })
        return Response(serializer.data)


class UserRegistration(UserViewSet):
    template_name = 'index.html'
    renderer_classes = [
        renderers.TemplateHTMLRenderer,

    ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'serializer': serializer})
        serializer.save()
        return HttpResponseRedirect(redirect_to='http://localhost:8000/')

''' TO BE EDITED
class LoginView(TemplateView):
    template_name = "registration/login.html"

    def dispatch(self, request, *args, **kwargs):
        context = {}
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                context['error'] = "Логин или пароль неправильные"
        return render(request, self.template_name, context)
'''
