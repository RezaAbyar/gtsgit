from django.contrib import admin
from .models import *
from jalali_date import datetime2jalali

admin.site.register(SarakKasri2)
admin.site.register(Certificate)
admin.site.register(CBrand)


@admin.register(Sells)
class SellsAdmin(admin.ModelAdmin):
    list_display = ('gs', 'get_create_date')
    list_filter = ['gs__area__zone', ]
    search_fields = ['gs__gsid', ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_create_date(self, obj):
        return datetime2jalali(obj.tarikh).strftime('%Y/%m/%d')
