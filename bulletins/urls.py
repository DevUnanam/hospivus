from django.urls import path
from bulletins import views

app_name = "bulletins"

urlpatterns = [
    # Event list and detail views
    path('events/', views.EventsListView.as_view(), name='events'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    
    # Event management (non-patients only)
    path('events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_edit'),
    path('events/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    
    # Event actions
    path('events/<int:event_id>/register/', views.register_for_event, name='register_event'),
    path('events/<int:event_id>/unregister/', views.unregister_from_event, name='unregister_event'),
    path('events/<int:event_id>/save/', views.save_event, name='save_event'),
    path('events/<int:event_id>/unsave/', views.unsave_event, name='unsave_event'),
]