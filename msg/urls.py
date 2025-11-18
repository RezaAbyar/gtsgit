from django.urls import path

from . import views

app_name = 'msg'

urlpatterns = [
    path('Inbox/<str:id>/', views.inbox, name='Inbox'),
    path('getRole/', views.getRole, name='getRole'),
    path('delmsg/<str:id>/', views.delmsg, name='delmsg'),
    path('setStar/<str:id>/', views.setStar, name='setStar'),
    path('isRead/', views.isRead, name='isRead'),
    path('replyMsg/', views.replyMsg, name='replyMsg'),
    path('msgevent/', views.msgevent, name='msgevent'),
    path('chat/', views.chat, name='chat'),
    path('msgmodal/', views.msgmodal, name='msgmodal'),
    ]