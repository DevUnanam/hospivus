from django.urls import path
from dm import views

app_name = "dm"

urlpatterns = [
    path('messages/', views.MessagesView.as_view(), name='messages'),
]
