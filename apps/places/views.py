from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from apps.main.permissions import (IsUploaderOrReadOnly,
                                   IsOwnerOrReadOnly,
                                   IsReviewerOrReadOnly)

from apps.places.models import Place, Event, Drink, PlaceUserReview
from apps.places.serializer import (PlaceSerializer,
                                    EventSerializer,
                                    DrinkSerializer,
                                    ReviewSerializer)


class PlaceTitleFilter(DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if 'title' in request.query_params:
            place_title = request.query_params['title']
            return queryset.filter(
                title__contains=place_title
            ).calculate_auto_fill_fields()
        return queryset

    class Meta:
        model = Place,
        fields = ('title', )


class PlaceViewSet(ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [IsUploaderOrReadOnly]
    filter_backends = [PlaceTitleFilter]
    filterset_fields = ['title', ]

    def get_queryset(self):
        return Place.objects.prefetch_related(
            'images',
            'events',
            'reviews__author'
        ).calculate_auto_fill_fields()


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['place', ]


class DrinkViewSet(ModelViewSet):
    queryset = Drink.objects.all()
    serializer_class = DrinkSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['place', ]


class ReviewViewSet(ModelViewSet):
    queryset = PlaceUserReview.objects.filter(is_visible=True)
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]
    # permission_classes = [IsReviewerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['place', 'rating', 'author', ]
