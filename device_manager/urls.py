from django.urls import path
from . import views

app_name = 'device_manager'

urlpatterns = [
    path('', views.device_list, name='device_list'),
    path('add/', views.add_device, name='add_device'),
    path('<int:device_id>/', views.device_detail, name='device_detail'),
    path('scan/', views.scan_devices, name='scan_devices'),
    path('<int:device_id>/check/', views.check_device_status, name='check_device_status'),
    path('emulators/', views.emulator_profiles, name='emulator_profiles'),
    path('emulators/<int:profile_id>/start/', views.start_emulator, name='start_emulator'),
] 