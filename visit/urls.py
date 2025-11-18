from django.urls import path
from . import views
from django.urls import path
from .views import (
    CertificateTypeListView, CertificateTypeCreateView, CertificateTypeUpdateView,
    CertificateDetailView
)

app_name = 'visit'

urlpatterns = [
    path('sarakkasri/<int:_id>/<int:_st>/', views.sarakkasriview, name='sarakkasri'),
    path('sarakkasrilist/', views.sarakkasrilist, name='sarakkasrilist'),
    path('listnazel/', views.listnazel, name='listnazel'),
    path('savesellsarak/', views.savesellsarak, name='savesellsarak'),
    path('loadsellsarak/', views.loadsellsarak, name='loadsellsarak'),
    path('certificate-types/', CertificateTypeListView.as_view(), name='certificate_type_list'),
    path('certificate-types/create/', CertificateTypeCreateView.as_view(), name='certificate_type_create'),
    path('certificate-types/<int:pk>/edit/', CertificateTypeUpdateView.as_view(), name='certificate_type_update'),

    path('certificates/', views.certificate_list_view, name='certificate_list'),
    path('certificates/create/', views.certificate_create_view, name='certificate_create'),
    path('certificates/<int:pk>/', CertificateDetailView.as_view(), name='certificate_detail'),

    path('emergency-fueling/create/', views.emergency_fueling_create, name='emergency_fueling_create'),
    path('emergency-permission/create/', views.emergency_permission_create, name='emergency_permission_create'),
    path('emergency-fueling/list/', views.emergency_fueling_list, name='emergency_fueling_list'),
    path('emergency-permission/list/', views.emergency_permission_list, name='emergency_permission_list'),
    path('check-duplicate-fueling/', views.check_duplicate_fueling, name='check_duplicate_fueling'),
]