from django.urls import path
from . import views
from rest_framework import routers
from .views_flutter import CardSearch,LoginView, LogoutView
from .liveinfo import GetLiveInfo, GetLiveBohran
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )




urlpatterns = [


    path('card-search/', CardSearch.as_view()),
#     path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

