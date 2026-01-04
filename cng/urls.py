from django.urls import path
from . import views

app_name = 'cng'

urlpatterns = [
    # جایگاه‌ها
    path('stations/', views.StationListView.as_view(), name='station_list'),
    path('stations/add/', views.StationCreateView.as_view(), name='station_create'),
    path('stations/<int:pk>/', views.StationDetailView.as_view(), name='station_detail'),
    path('stations/<int:pk>/edit/', views.StationUpdateView.as_view(), name='station_update'),
    path('stations/<int:pk>/delete/', views.StationDeleteView.as_view(), name='station_delete'),

    # تجهیزات
    path('stations/<int:station_id>/equipments/', views.EquipmentListView.as_view(), name='equipment_list'),
    path('stations/<int:station_id>/equipments/add/', views.EquipmentCreateView.as_view(), name='equipment_create'),

    # AJAX endpoints
    path('ajax/get-areas/', views.get_areas_by_region, name='get_areas'),
    path('ajax/get-cities/', views.get_cities_by_area, name='get_cities'),
    path('stations/<int:station_id>/meters/create/', views.meter_create, name='meter_create'),
]