"""
URL configuration for facebook_bot project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bot_dashboard.urls')),
    path('devices/', include('device_manager.urls')),
    path('tasks/', include('task_engine.urls')),
    path('api/', include('bot_dashboard.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 