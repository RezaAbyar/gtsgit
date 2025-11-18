from django.contrib import admin
from jalali_date import datetime2jalali
import jdatetime

from .models import PayBaseParametrs, Post, Payroll, StatusRef, StatusStore, Store, StoreList, StoreHistory, PayItems, \
    PayParametr, PayDarsadMah, TekKarkard, MozdSanavat, BaseGroup, BaseDetail, RepairStoreName, Repair, RepairStore, \
    RepairRole, InsertPayroll, PersonPayment, ZoneToStorage, StoreManufacturer, SerialRange, kargahToStorage, \
    GenerateSerialNumber
from .models_repaire import RepaireStores, Repaires


class PayBaseParametrsAdmin(admin.ModelAdmin):
    list_display = ('name', 'count', 'price', 'sortable',)
    list_editable = ('sortable',)


class PayRollAdmin(admin.ModelAdmin):
    list_display = ('period', 'tek', 'accept', 'paybaseparametrs', 'accepttedad')
    list_editable = ('accept',)
    list_filter = ['period', 'tek__zone', 'paybaseparametrs__name', 'accepttedad']


class KarkardAdmin(admin.ModelAdmin):
    list_display = ('period', 'tek', 'value',)
    list_editable = ('value',)
    list_filter = ['period', 'tek__zone']


class PayStore(admin.ModelAdmin):
    list_display = ('get_create_date', 'pinpad', 'master', 'storage', 'zone', 'status')
    list_filter = ['zone', 'storage', 'status']
    list_editable = ('status',)

    def get_create_date(self, obj):
        return datetime2jalali(obj.tarikh).strftime('%Y/%m/%d')

    get_create_date.admin_order_field = 'tarikh'


@admin.register(RepairRole)
class RepairRoleAdmin(admin.ModelAdmin):
    list_display = (
        'storage', 'repairstore', 'minvalue', 'startvalue', 'usevalue', 'ofroadvalue', 'inventory', 'required', 'tedad')
    list_filter = ('storage',)


@admin.register(StoreHistory)
class StoreHistoryAdmin(admin.ModelAdmin):
    list_display = ('get_jalali_date', 'store', 'description', 'owner', 'status', 'information', 'baseroot', 'storage','activeday')
    search_fields = ('store__serial',)
    list_per_page = 10

    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]




    def get_jalali_date(self, obj):
        jdate = jdatetime.GregorianToJalali(obj.create.year, obj.create.month, obj.create.day)
        return jdatetime.datetime(jdate.jyear, jdate.jmonth, jdate.jday, obj.create.hour, obj.create.minute)

    get_jalali_date.short_description = 'تاریخ'


@admin.register(PersonPayment)
class PersonPaymentAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'mablagh', 'price', 'baseparametr', 'owner', 'tadil')
    list_filter = ('baseparametr__name', 'start_date__mount')
    search_fields = ['owner__codemeli', ]


@admin.register(ZoneToStorage)
class ZoneToStorageAdmin(admin.ModelAdmin):
    list_display = ('zone', 'storage',)
    list_filter = ('zone',)
    search_fields = ['zone', ]


@admin.register(kargahToStorage)
class kargahToStorageAdmin(admin.ModelAdmin):
    list_display = ('zone', 'storage',)
    list_filter = ('zone',)
    search_fields = ['zone', ]


@admin.register(Repair)
class RepairAdmin(admin.ModelAdmin):
    list_display = ('storage', 'repairstore', 'tarikh', 'get_jalali_date', 'valuecount')
    list_filter = ('storage',)

    def get_jalali_date(self, obj):
        jdate = jdatetime.GregorianToJalali(obj.tarikh.year, obj.tarikh.month, obj.tarikh.day)
        return jdatetime.datetime(jdate.jyear, jdate.jmonth, jdate.jday, obj.create.hour, obj.create.minute)

    get_jalali_date.short_description = 'تاریخ'

class PayItemsAdmin(admin.ModelAdmin):
    list_display = ('paybase', 'info', 'ename', 'storage',)
    list_filter = ['paybase', 'storage']
    list_editable = ('ename',)


class PayParametrsAdmin(admin.ModelAdmin):
    list_display = ('tek', 'period', 'payitem', 'inputval',)
    list_filter = ['period', 'tek__zone']

class SerialRangeAdmin(admin.ModelAdmin):
    list_display = ('serialnumber',)
    search_fields = ['serialnumber', ]



class StoreListAdmin(admin.ModelAdmin):
    list_display = ('zone', 'status', 'statusstore', 'zone', 'pdate', 'serial',)
    list_filter = ['update', 'zone', 'status', 'statusstore']
    list_editable = ('status', 'serial',)
    search_fields = ['serial', ]

    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_change_permission(self, request, obj=None):
        if request.method not in ('GET', 'HEAD', 'POST'):
            return False
        return super(StoreListAdmin, self).has_change_permission(request, obj)


admin.site.register(PayBaseParametrs, PayBaseParametrsAdmin)
admin.site.register(PayItems, PayItemsAdmin)
admin.site.register(Payroll, PayRollAdmin)
admin.site.register(PayParametr, PayParametrsAdmin)
admin.site.register(PayDarsadMah)
admin.site.register(StatusRef)
admin.site.register(StatusStore)
admin.site.register(Store, PayStore)
admin.site.register(StoreList, StoreListAdmin)

admin.site.register(Post)
admin.site.register(TekKarkard, KarkardAdmin)
admin.site.register(MozdSanavat)
admin.site.register(BaseGroup)
admin.site.register(BaseDetail)
admin.site.register(RepairStore)
admin.site.register(RepairStoreName)
admin.site.register(InsertPayroll)
admin.site.register(RepaireStores)
admin.site.register(Repaires)
admin.site.register(StoreManufacturer)
admin.site.register(GenerateSerialNumber)
admin.site.register(SerialRange, SerialRangeAdmin)
