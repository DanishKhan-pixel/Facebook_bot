"""
URL configuration for facebook_bot project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def redirect_to_login(request):
    """Redirect root URL to login page"""
    return redirect('bot_dashboard:login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_login, name='root'),
    path('dashboard/', include('bot_dashboard.urls')),
    path('devices/', include('device_manager.urls')),
    path('tasks/', include('task_engine.urls')),
    path('api/', include('bot_dashboard.api_urls')),
    # Redirect swagger to login
    path('swagger/', redirect_to_login, name='swagger_redirect'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 