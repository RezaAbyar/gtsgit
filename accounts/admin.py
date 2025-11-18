from django.contrib import admin
from .models import Captcha, Visits, Logs
import jdatetime


@admin.register(Visits)
class VisistAdmin(admin.ModelAdmin):
    list_display = ('REMOTE_HOST', 'REMOTE_ADDR', 'HTTP_REFERER', 'get_jalali_date', 'QUERY_STRING')
    list_filter = ('create',)
    search_fields = ['HTTP_REFERER', 'REMOTE_HOST']

    def get_jalali_date(self, obj):
        jdate = jdatetime.GregorianToJalali(obj.create.year, obj.create.month, obj.create.day)
        return jdatetime.datetime(jdate.jyear, jdate.jmonth, jdate.jday, obj.create.hour, obj.create.minute)

    get_jalali_date.short_description = 'تاریخ'

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Logs)
class LogsAdmin(admin.ModelAdmin):
    list_display = ('get_jalali_date', 'owner', 'parametr1', 'parametr2','gs','macaddress')
    # list_filter = ('owner',)
    search_fields = ['owner__codemeli','gs' ]

    def get_jalali_date(self, obj):
        jdate = jdatetime.GregorianToJalali(obj.create.year, obj.create.month, obj.create.day)
        return jdatetime.datetime(jdate.jyear, jdate.jmonth, jdate.jday, obj.create.hour, obj.create.minute)

    get_jalali_date.short_description = 'تاریخ'

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False




@admin.register(Captcha)
class CaptchaAdmin(admin.ModelAdmin):
    list_display = ('number', 'img')
    readonly_fields = ('number', 'img')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


