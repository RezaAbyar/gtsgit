from django.urls import path
from . import views
from base import autoexcel

app_name = 'bazrasnegar'

urlpatterns = [
    path('search/', views.search_bazras_negar, name='bazrasnegar_search'),
    path('add/', views.bazras_negar_create, name='bazrasnegar_add'),
    path('<int:message_id>/', views.image_viewer, name='image_viewer'),
    path('<int:message_id>/<int:page_number>/', views.image_viewer, name='image_viewer_page'),
]
