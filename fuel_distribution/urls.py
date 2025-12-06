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
]