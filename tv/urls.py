from django.urls import path
from tv import views

app_name = "tv"

urlpatterns = [
    path('tv/', views.TvView.as_view(), name='tv'),
    path('category/<slug:category_slug>/', views.CategoryVideosView.as_view(), name='category'),
    path('video/<slug:slug>/', views.VideoDetailView.as_view(), name='video_detail'),
]