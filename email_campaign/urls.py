from django.urls import path
from email_campaign import views

app_name = "email_campaign"

urlpatterns = [
    path('campaign/', views.EmailCampaignView.as_view(), name='email_campaign'),
    path('campaign/contact/', views.contact_view, name='contact_us'),
    path('campaign/send-promotional/', views.send_promotional_email, name='send_promotional_email'),
    path('campaign/unsubscribe/', views.unsubscribe_view, name='unsubscribe_email'),
]