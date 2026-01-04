from django.urls import path
from . import views

app_name = 'fuel_distribution'

urlpatterns = [
    # عمومی
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/create/', views.create_profile, name='profile_create'),

    # واردکننده
    path('imports/', views.import_list, name='import_list'),
    path('imports/create/', views.import_create, name='import_create'),
    path('imports/<int:pk>/', views.import_detail, name='import_detail'),
    path('imports/<int:pk>/edit/', views.import_update, name='import_update'),
    path('imports/<int:pk>/delete/', views.import_delete, name='import_delete'),
    path('imports/<int:pk>/confirm/', views.import_confirm, name='import_confirm'),

    # توزیع از واردکننده به توزیع‌کننده
    path('distributions/', views.distribution_list, name='distribution_list'),
    path('distributions/create/', views.distribution_create, name='distribution_create'),
    path('distributions/<int:pk>/', views.distribution_detail, name='distribution_detail'),

    # توزیع‌کننده
    path('distributor/received-fuel/', views.received_fuel_list, name='received_fuel_list'),
    path('distributor/stations/', views.distributor_stations, name='distributor_stations'),
    path('distributor/stations/create/', views.station_create, name='station_create'),
    path('distributor/stations/<int:pk>/', views.station_detail, name='station_detail'),
    path('distributor/deliveries/', views.delivery_list, name='delivery_list'),
    path('distributor/deliveries/create/', views.delivery_to_station_create, name='delivery_to_station_create'),
    path('distributor/deliveries/<int:pk>/', views.delivery_detail, name='delivery_detail'),
    path('distributor/deliveries/<int:pk>/confirm/', views.delivery_confirm, name='delivery_confirm'),
    path('distributor/deliveries/create/<int:station_id>/', views.delivery_to_station_create,
         name='delivery_to_station_create_for_station'),

    # گزارش‌ها
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/generate/', views.generate_import_report_view, name='generate_report'),
    path('reports/list/', views.report_list, name='report_list'),
    path('reports/<int:pk>/', views.report_detail, name='report_detail'),

    # موجودی
    path('stock/', views.stock_management, name='stock_management'),
    path('stock/history/', views.stock_history, name='stock_history'),

    # API
    path('api/import/<int:import_id>/remaining/', views.get_import_remaining_amount, name='api_import_remaining'),
    path('api/distributor/stock/', views.get_distributor_stock, name='api_distributor_stock'),
    path('api/search/distributors/', views.search_distributors, name='api_search_distributors'),
    path('api/search/gas-stations/', views.search_gas_stations, name='api_search_gas_stations'),

    path('supplier/dashboard/', views.supplier_dashboard, name='supplier_dashboard'),
    path('supplier/daily-price/', views.daily_price_management, name='daily_price_management'),
    path('supplier/nozzle-sales/', views.nozzle_sales_management, name='nozzle_sales_management'),
    path('supplier/tank-inventory/', views.tank_inventory_management, name='tank_inventory_management'),
    path('supplier/pending-deliveries/', views.pending_deliveries, name='pending_deliveries'),
    path('supplier/delivery-receipt/<int:pk>/', views.delivery_receipt, name='delivery_receipt'),
    path('supplier/daily-summary/', views.daily_summary, name='daily_summary'),
    path('supplier/nozzle-sales-list/', views.nozzle_sales_list, name='nozzle_sales_list'),
    path('supplier/inventory-history/', views.inventory_history, name='inventory_history'),

    # API URLs
    path('api/daily-summary/', views.get_daily_summary_ajax, name='get_daily_summary_ajax'),
    path('api/today-prices/', views.get_today_prices_ajax, name='get_today_prices_ajax'),
    path('api/nozzle-last-counter/<int:nozzle_id>/', views.get_nozzle_last_counter_ajax,
         name='get_nozzle_last_counter_ajax'),

    path('change-current-station/', views.change_current_station, name='change_current_station'),
    path('set-active-station/<int:station_id>/', views.set_active_station, name='set_active_station'),
    path('quick-change-station/', views.quick_change_station, name='quick_change_station'),

    path('management-sales-report/', views.management_sales_report, name='management_sales_report'),
    path('management-sales-report/export/', views.export_management_report, name='export_management_report'),
]