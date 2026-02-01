from django.urls import path
from core import views
from email_campaign.views import EmailCampaignView

app_name = "core"

urlpatterns = [
    path('landing/', views.LandingPageView.as_view(), name='landing_page'),
    path('', EmailCampaignView.as_view(), name='landing_page_temp'),
    path('home/', views.home, name='home'),
    path('health/', views.HealthView.as_view(), name='health'),
    path('help/', views.HelpView.as_view(), name='help'),
    path('doctors/search/', views.search_doctors, name='search_doctors'),
]
