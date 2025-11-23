from .models import SellModel, IpcLog, SellGs, AccessChangeSell, InfoEkhtelafLogs, CarInfo, CarStatus, EditSell, \
    AcceptForBuy, Mojodi, Oildepot, ParametrGs, SellGsInHour, OpenCloseSell, CloseSellReport, ModemDisconnect, \
    ProductId, Waybill, DiscrepancyApproval, SendType, ReceivedBarname, Sender, ConsumptionPolicy, QRScan, SellTime
from django.contrib import admin
from jalali_date import datetime2jalali
import jdatetime
from sell.qrreader import load_code


class SellModelAdmin(admin.ModelAdmin):
    list_display = (
        'gs_id', 'pumpnumber', 'sell', 'sellkol', 'tarikh', 'product_id', 'nomojaz', 'nomojaz2', 'mindatecheck',
        'islocked')
    search_fields = ['gs__gsid', ]
    ordering = ('-tarikh', '-id')


class IPCModelAdmin(admin.ModelAdmin):
    list_display = ('gsid', 'dore', 'date_ipc', 'rpm_version', 'rpm_version_date', 'pt_version', 'blacklist_version',
                    'blacklist_count', 'zone_table_version', 'update')
    list_filter = ('gsid', 'rpm_version')
    search_fields = ['gs__gsid']


@admin.register(AccessChangeSell)
class AccessChangeSellAdmin(admin.ModelAdmin):
    list_display = ('gs', 'tarikh', 'pump')
    list_filter = ['gs__area__zone', ]
    search_fields = ['gs__gsid', ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ModemDisconnect)
class ModemDisconnectAdmin(admin.ModelAdmin):
    list_display = ('gs', 'tarikh', 'starttime', 'endtime', 'ip')
    list_filter = ['gs__area__zone', ]
    search_fields = ['gs__gsid', ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(OpenCloseSell)
class OpenCloseSellAdmin(admin.ModelAdmin):
    list_display = ('gs', 'tarikh', 'owner', 'status', 'get_jalali_date')
    list_filter = ['gs__area__zone']
    search_fields = ['gs__gsid', ]

    def get_jalali_date(self, obj):
        jdate = jdatetime.GregorianToJalali(obj.created_at.year, obj.created_at.month, obj.created_at.day)
        return jdatetime.datetime(jdate.jyear, jdate.jmonth, jdate.jday, obj.created_at.hour, obj.created_at.minute)

    get_jalali_date.short_description = 'تاریخ انجام عملیات'

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(EditSell)
class EditSellAdmin(admin.ModelAdmin):
    list_display = ('owner', 'tarikh', 'sell', 'old', 'new', 'status')
    list_filter = ['sell__gs__area__zone', ]
    search_fields = ['sell__gs__gsid', ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SellGs)
class StoreListAdmin(admin.ModelAdmin):
    list_display = ('gs', 'tarikh', 'product', 'sell', 'yarane', 'azad', 'ezterari')
    list_filter = ['gs__area__zone', 'product']
    search_fields = ['gs__gsid', ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(InfoEkhtelafLogs)
class StoreListAdmin(admin.ModelAdmin):
    list_display = ('tarikh', 'pomp', 'status', 'owner',)
    list_filter = ['sell__gs__area__zone', ]
    search_fields = ['sell__gs__gsid', ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AcceptForBuy)
class AcceptForBuyAdmin(admin.ModelAdmin):
    list_display = ('gs', 'tarikh')
    search_fields = ['gs__gsid', 'tarikh', ]


@admin.register(CarInfo)
class CarInfoAdmin(admin.ModelAdmin):
    list_display = ('tarikh', 'carstatus', 'amount', 'gs',)
    search_fields = ['gs__gsid', 'tarikh', ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Oildepot)
class OildepotAdmin(admin.ModelAdmin):
    list_display = ('zone', 'name')


@admin.register(ParametrGs)
class ParametrGsAdmin(admin.ModelAdmin):
    list_display = ('gs', 'oildepot')
    autocomplete_fields = ('gs',)


@admin.register(Mojodi)
class ParametrGsAdmin(admin.ModelAdmin):
    list_display = ('gs', 'tarikh', 'benzin', 'super', 'gaz', 'uniq')
    search_fields = ['gs__gsid', ]
    list_editable = ['benzin', 'super', 'gaz']


@admin.register(Sender)
class SenderAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'location')
    search_fields = ['code', ]
    list_editable = ['location']


def start_batch(batch: QRScan):
    load_code(
        f'1:1:{batch.qr_data1}',
        batch.owner.id)
    return True


@admin.register(QRScan)
class SenderAdmin(admin.ModelAdmin):
    actions = ['start_batch_action']
    list_display = ('gs', 'dore', 'get_jalali_date', 'owner')
    search_fields = ['gs__gsid', ]

    def start_batch_action(self, request, queryset):
        for obj in queryset:
            start_batch(obj)
        self.message_user(request, f"Started working for {queryset.count()} batch(es).", 'info')

    start_batch_action.short_description = "Start batch"

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_jalali_date(self, obj):
        jdate = jdatetime.GregorianToJalali(obj.created_at.year, obj.created_at.month, obj.created_at.day)
        return jdatetime.datetime(jdate.jyear, jdate.jmonth, jdate.jday, obj.created_at.hour, obj.created_at.minute)


admin.site.register(SellModel, SellModelAdmin),
admin.site.register(IpcLog, IPCModelAdmin),
admin.site.register(CarStatus),
admin.site.register(SellGsInHour),
admin.site.register(Waybill),
admin.site.register(SendType),
admin.site.register(ReceivedBarname),
admin.site.register(ConsumptionPolicy),
admin.site.register(SellTime),


@admin.register(CloseSellReport)
class ParametrGsAdmin(admin.ModelAdmin):
    list_display = ('owner', 'gs', 'tarikh', 'status', 'created_at')
    search_fields = ['gs__gsid', ]


@admin.register(ProductId)
class ProductIdAdmin(admin.ModelAdmin):
    list_display = ('product', 'productid', 'name')


@admin.register(DiscrepancyApproval)
class DiscrepancyApprovaldAdmin(admin.ModelAdmin):
    list_display = ('get_zone', 'get_gsid', 'get_gs', 'get_pomp', 'discrepancy_date', 'discrepancy_amount',)

    def get_zone(self, obj):
        return obj.sell.gs.area.zone.name if obj.sell else '-'

    def get_gsid(self, obj):
        return obj.sell.gs.gsid if obj.sell else '-'

    def get_gs(self, obj):
        return obj.sell.gs.name if obj.sell else '-'

    def get_pomp(self, obj):
        return obj.sell.pumpnumber if obj.sell else '-'
