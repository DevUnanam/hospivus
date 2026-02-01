from django.urls import path
from bulletins import views

app_name = "bulletins"

urlpatterns = [
    path('events/', views.EventsView.as_view(), name='events'),
]