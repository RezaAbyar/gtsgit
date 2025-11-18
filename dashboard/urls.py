from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_main, name='main'),
    path('api/sales-data/', views.get_sales_data, name='sales_data'),
    path('api/inventory-data/', views.get_inventory_data, name='inventory_data'),
    path('api/kpi-data/', views.get_kpi_data, name='kpi_data'),
    path('api/station-ranking/', views.get_station_ranking, name='station_ranking'),
    path('api/waybill-chart/', views.get_waybill_chart_data, name='waybill_chart'),
    path('api/sales-chart/', views.get_sales_chart_data, name='sales_chart'),
    path('api/inventory-chart/', views.get_inventory_chart_data, name='inventory_chart'),
    path('api/filter-options/', views.get_filter_options, name='filter_options'),
    path('map/', views.gs_map_view, name='gs_map'),
]