from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from apps.main.permissions import (IsUploaderOrReadOnly,
                                   IsOwnerOrReadOnly,
                                   IsReviewerOrReadOnly)

from apps.places.models import Place, Event, Drink, PlaceUserReview
from apps.places.serializer import (PlaceSerializer,
                                    EventSerializer,
                                    DrinkSerializer,
                                    ReviewSerializer)


class OwnerPlaceFilter(DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if 'uploaded_by' in request.query_params:
            uploaded_by = request.query_params['uploaded_by']
            return queryset.filter(uploaded_by=uploaded_by)\
                .calculate_average_price()\
                .calculate_rating()
        return queryset

    class Meta:
        model = Place,
        fields = ('uploaded_by',)


class PlaceViewSet(ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [IsUploaderOrReadOnly]
    filter_backends = [OwnerPlaceFilter]
    filterset_fields = ['uploaded_by', ]

    def get_object(self):
        place_id = super(PlaceViewSet, self).get_object().id
        obj = Place.objects.filter(
            id=place_id
        ).calculate_average_price().calculate_rating()[0]
        return obj

    def get_queryset(self):
        return Place.objects.calculate_average_price().calculate_rating()


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
    queryset = PlaceUserReview.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['place', 'rating', 'author', ]
