from django.urls import path
from . import views
from rest_framework.authtoken import views as auth_token
from .views import DefaultRole, GetRole

app_name = 'accounts'

urlpatterns = [
    path('DefaultRole/', DefaultRole.as_view(), name='DefaultRole'),
    path('GetRole/', GetRole.as_view(), name='GetRole'),
    path('change/', views.change_password, name='change'),
    path('password_change/<str:id>/', views.password_change, name='password_change'),
    path('MyProfile', views.myprofile, name='MyProfile'),
    path('profileItems', views.profileitems, name='profileItems'),
    path('Roles', views.roles, name='Roles'),
    path('addDefualtaccesslist', views.adddefualtaccesslist, name='addDefualtaccesslist'),
    path('userAccess/<str:id>/', views.useraccess, name='userAccess'),
    path('remove_user_permission/<int:id>/', views.remove_user_permission, name='remove_user_permission'),
    path('api-token-auth/', auth_token.obtain_auth_token),
    path('userlogs/', views.userlogs, name='userlogs'),
    path('checkmobailfa/', views.checkmobailfa, name='checkmobailfa'),
    path('usergroupnemodar/', views.usergroupnemodar, name='usergroupnemodar'),
    path('recover_password/', views.recoverpassword, name='recover_password'),
    path('reportuser/', views.reportuser, name='reportuser'),
    path('access_management_view/', views.access_management_view, name='access_management_view'),
    path('edit_permission/<int:id>/', views.edit_permission_view, name='edit_permission'),

]
