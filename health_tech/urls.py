from django.urls import path
from . import views

app_name = 'health_tech'

urlpatterns = [
    # A-Z conditions index
    path('conditions/', views.conditions_index, name='conditions_index'),
    
    # Conditions by letter
    path('conditions/<str:letter>/', views.conditions_by_letter, name='conditions_by_letter'),
    
    # Condition detail
    path('conditions/detail/<slug:slug>/', views.ConditionDetailView.as_view(), name='condition_detail'),
    
    # Search
    path('conditions/search/', views.search_conditions, name='search_conditions'),
]