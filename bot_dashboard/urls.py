from django.urls import path
from . import views

app_name = 'bot_dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', views.settings_view, name='settings'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/start/', views.start_task, name='start_task'),
    path('tasks/<int:task_id>/stop/', views.stop_task, name='stop_task'),
    path('tasks/<int:task_id>/download/', views.download_ids, name='download_ids'),
    path('logs/', views.logs_view, name='logs'),
] 