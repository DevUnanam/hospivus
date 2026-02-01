"""
URL mappings for the user API.
"""
from django.urls import path
from accounts.api import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


app_name = 'accounts_api'

urlpatterns = [
    path("health-check/", views.health_check, name="health-check"),
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('profile/', views.ManageUserView.as_view(), name='profile'),
    path("token/", TokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
