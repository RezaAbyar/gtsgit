from django.urls import path
from . import views

app_name = 'pm'

urlpatterns = [
    path('<int:pk>/', views.station_detail, name='station_detail'),
    path('<int:station_pk>/checklist/create/', views.create_checklist, name='create_checklist'),
    path('checklist/<int:pk>/', views.checklist_detail, name='checklist_detail'),
]


