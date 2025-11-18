from django.contrib import admin
from .models import *


class PanModelsAdmin(admin.ModelAdmin):
    list_display = ['pan', 'statuspan', 'tarikhShamsi', 'gs', 'user', 'nahye']
    list_filter = ('gs',)
    search_fields = ['pan', ]


class PanHistoryAdmin(admin.ModelAdmin):
    list_display = ['pan', 'status', 'user', 'persiandate']
    list_filter = ('user',)
    search_fields = ['pan__pan', ]


admin.site.register(StatusPan),
admin.site.register(ValidPan),
admin.site.register(PanModels, PanModelsAdmin),
admin.site.register(PanHistory, PanHistoryAdmin),
admin.site.register(StatusCardAzad),
admin.site.register(CardAzad),