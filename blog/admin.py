from django.contrib import admin
from .models import Tags, Videos, VideoProvider


@admin.register(Videos)
class LockModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'views')
    list_filter = ['tags']

admin.site.register(Tags)
admin.site.register(VideoProvider)
