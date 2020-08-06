from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from django.contrib.auth.models import User
from apps.users.serializer import UserRegistrationSerializer


class UserViewSet(mixins.CreateModelMixin,
                  GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
