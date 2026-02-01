from django.urls import path
from accounts import views
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

app_name = "accounts"

urlpatterns = [
    path('register/', views.SignUpView.as_view(), name='register_user'),
    path('login/', views.SignInView.as_view(), name='login_user'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
]
