from rest_framework import routers

from apps.users.views import UserViewSet
from apps.places.views import PlaceViewSet, EventViewSet, DrinkViewSet, ReviewViewSet

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('places', PlaceViewSet, basename='places')
router.register('events', EventViewSet, basename='events')
router.register('drinks', DrinkViewSet, basename='drinks')
router.register('reviews', ReviewViewSet, basename='reviews')
