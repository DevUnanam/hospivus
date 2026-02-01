from django.urls import path
from tasks import views

app_name = "tasks"

urlpatterns = [
    path('tasks/', views.TasksView.as_view(), name='tasks'),
]