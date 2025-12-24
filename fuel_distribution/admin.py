from django.contrib import admin
from django.utils.html import format_html
from .models import (
    UserDistributionProfile, SuperFuelImport, ImportToDistributor,
    DistributorGasStation, DistributionToGasStation, FuelStock,
    FuelDistributionReport, SuperModel, Nazel
)


admin.site.register(SuperModel)
admin.site.register(Nazel)

@admin.register(UserDistributionProfile)
class UserDistributionProfileAdmin(admin.ModelAdmin):
    list_display = ['owner', 'get_full_name', 'role', 'company', 'is_active']
    list_filter = ['role', 'is_active', 'company']
    search_fields = ['owner__name', 'owner__lname', 'owner__codemeli']

    def get_full_name(self, obj):
        return obj.owner.get_full_name()

    get_full_name.short_description = 'نام کامل'


@admin.register(SuperFuelImport)
class SuperFuelImportAdmin(admin.ModelAdmin):
    list_display = [
        'import_date', 'importer', 'company', 'amount_liters',
        'tracking_number', 'status', 'remaining_amount_display'
    ]
    list_filter = ['status', 'import_date', 'company']
    search_fields = ['tracking_number', 'document_number', 'importer__name']
    readonly_fields = ['created_at', 'updated_at']

    def remaining_amount_display(self, obj):
        return f"{obj.remaining_amount} لیتر"

    remaining_amount_display.short_description = 'مقدار باقی‌مانده'


@admin.register(ImportToDistributor)
class ImportToDistributorAdmin(admin.ModelAdmin):
    list_display = [
        'distribution_date', 'fuel_import', 'distributor',
        'distributor_company', 'amount_liters', 'price_per_liter'
    ]
    list_filter = ['distribution_date', 'distributor_company']
    search_fields = ['document_number', 'distributor__name']


@admin.register(DistributorGasStation)
class DistributorGasStationAdmin(admin.ModelAdmin):
    list_display = ['distributor', 'gas_station', 'start_date', 'is_active']
    list_filter = ['is_active', 'start_date']
    search_fields = ['gas_station__name', 'distributor__name']


@admin.register(DistributionToGasStation)
class DistributionToGasStationAdmin(admin.ModelAdmin):
    list_display = [
        'delivery_date', 'distributor_distribution',
        'distributor_gas_station', 'amount_liters',
        'status', 'received_confirmation'
    ]
    list_filter = ['status', 'delivery_date', 'received_confirmation']
    search_fields = ['delivery_document', 'driver_info']


@admin.register(FuelStock)
class FuelStockAdmin(admin.ModelAdmin):
    list_display = [
        'company', 'current_stock', 'total_imported',
        'total_distributed', 'last_updated'
    ]
    list_filter = ['company']
    readonly_fields = ['last_updated']


@admin.register(FuelDistributionReport)
class FuelDistributionReportAdmin(admin.ModelAdmin):
    list_display = [
        'report_type', 'period_start', 'period_end',
        'company', 'generated_by', 'created_at'
    ]
    list_filter = ['report_type', 'created_at']
    search_fields = ['generated_by__name']
    readonly_fields = ['created_at']
