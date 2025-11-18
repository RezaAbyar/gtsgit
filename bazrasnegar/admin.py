from django.contrib import admin
from .models import *


@admin.register(BazrasNegar)
class BazrasNegarAdmin(admin.ModelAdmin):
    list_display = ('number', 'tarikh', 'info', 'title', 'file')
