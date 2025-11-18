# stations/admin.py
from django.contrib import admin
from .models import  PMChecklist


class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'area', 'gsid', 'owner_name', 'owner_phone')
    search_fields = ('name', 'gsid', 'owner_name', 'owner_phone')
    list_filter = ('region', 'area')


class PMChecklistAdmin(admin.ModelAdmin):
    list_display = ('station', 'check_date', 'technician', 'next_check_date', 'ups_working')
    search_fields = ('station__name', 'technician__username')
    list_filter = ('check_date', 'ups_working', 'has_ups')
    date_hierarchy = 'check_date'



admin.site.register(PMChecklist, PMChecklistAdmin)
