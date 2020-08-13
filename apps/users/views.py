from django.http import HttpResponseRedirect
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, renderers

from django.contrib.auth.models import User
from apps.users.serializer import UserRegistrationSerializer


class UserViewSet(mixins.CreateModelMixin,
                  GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    template_name = 'index.html'
    renderer_classes = [
        renderers.BrowsableAPIRenderer,
        renderers.JSONRenderer,
        renderers.TemplateHTMLRenderer,
    ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'serializer': serializer})
        serializer.save()
        return HttpResponseRedirect(redirect_to='http://localhost:8000/')
