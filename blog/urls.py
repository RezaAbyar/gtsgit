from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog, name='blog'),
    path('play/<int:_id>/', views.videoplay, name='play'),
    path('tag/<str:_en>/', views.videotags, name='tag'),
]
