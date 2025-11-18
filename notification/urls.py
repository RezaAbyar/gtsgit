from django.urls import path
from . import views

app_name = 'notification'

urlpatterns = [

    path('save_subscription/', views.save_subscription, name='save_subscription'),
    path('notify_all_users/', views.notify_all_users, name='notify_all_users'),
    ]