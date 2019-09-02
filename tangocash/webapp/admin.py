from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import Advertisement, Review, Currency, Profile

@admin.register(Advertisement)
class AdvertisementAdmin(OSMGeoAdmin):
    list_display = ('ad_text', 'trader', 'location_name', 'location_point', 'post_date')

admin.site.register(Currency)
admin.site.register(Review)
admin.site.register(Profile)
