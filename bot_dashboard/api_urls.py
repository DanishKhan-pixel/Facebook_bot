from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('dashboard/stats/', views.api_dashboard_stats, name='dashboard_stats'),
    path('tasks/<int:task_id>/status/', views.api_task_status, name='task_status'),
] 