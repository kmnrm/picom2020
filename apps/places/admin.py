from django.contrib import admin
from django.utils.html import format_html

from apps.places.models import Place, PlaceImage, Event, PlaceUserReview
from adminsortable2.admin import SortableInlineAdminMixin


class PlaceImageInline(SortableInlineAdminMixin, admin.TabularInline):
    model = PlaceImage
    fields = ['image', 'get_preview',]
    readonly_fields = ['get_preview']
    extra = 0

    def get_preview(self, place):
        return format_html('<img src="{url}" height="100" />'.format(url=place.image.url))


class EventInline(admin.StackedInline):
    model = Event
    fieldsets = (
        ('Event Info', {
            'classes': ('collapse',),
            'fields': (
                ('title', 'get_preview', 'fee', 'image', ),
                ('date', 'time_from', 'time_till', ),
                'description',
            )
        }),
    )
    readonly_fields = ['get_preview']
    extra = 0

    def get_preview(self, event):
        return format_html('<img src="{url}" height="100" />'.format(url=event.image.url))


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Main Info', {
            'fields': (
                'uploaded_by',
                ('title', 'category', 'address', 'pinyin_address', 'phone_number'),
                ('logo', 'description'),
                ('opening_hours', 'closing_hours'),
                'police_rating',
            )
        }),
        ('Additional Info', {
            'classes': ('extrapretty',),
            'fields': ('average_price', ('latitude', 'longitude',),)
        }),
    )
    readonly_fields = ('average_price', 'pinyin_address')
    radio_fields = {"police_rating": admin.VERTICAL}
    inlines = [
        PlaceImageInline,
        EventInline,
    ]


@admin.register(PlaceUserReview)
class ReviewAdmin(admin.ModelAdmin):
    fields = (
        ('place', 'author', 'rating'),
        'text',
        'published_at',
    )
    readonly_fields = [
        'place',
        'author',
        'rating',
        'text',
        'published_at'
    ]
