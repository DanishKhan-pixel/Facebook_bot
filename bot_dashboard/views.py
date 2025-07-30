from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
import logging

logger = logging.getLogger(__name__)

from .models import (
    UserProfile, BotSettings, BotTask, CreatedFacebookID, 
    ActivityLog, SystemLog
)
from .forms import LoginForm, BotSettingsForm, BotTaskForm
from task_engine.tasks import start_bot_task, stop_bot_task
from device_manager.models import DeviceSession


def login_view(request):
    if request.user.is_authenticated:
        return redirect('bot_dashboard:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Log the login action
                ActivityLog.objects.create(
                    task=None,
                    level='info',
                    message=f'User {username} logged in successfully',
                    user=user
                )
                next_url = request.GET.get('next', 'bot_dashboard:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    
    return render(request, 'bot_dashboard/login.html', {'form': form})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('bot_dashboard:dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the registration
            ActivityLog.objects.create(
                task=None,
                level='info',
                message=f'New user {user.username} registered successfully',
                user=user
            )
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('bot_dashboard:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'bot_dashboard/signup.html', {'form': form})


@login_required
def logout_view(request):
    # Log the logout action
    ActivityLog.objects.create(
        task=None,
        level='info',
        message=f'User {request.user.username} logged out',
        user=request.user
    )
    logout(request)
    return redirect('bot_dashboard:login')


@login_required
def dashboard(request):
    # Get user profile or create one
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get recent tasks
    recent_tasks = BotTask.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    
    # Get active tasks
    active_tasks = BotTask.objects.filter(
        created_by=request.user,
        status__in=['pending', 'running']
    )
    
    # Get statistics
    total_tasks = BotTask.objects.filter(created_by=request.user).count()
    completed_tasks = BotTask.objects.filter(
        created_by=request.user,
        status='completed'
    ).count()
    total_ids_created = CreatedFacebookID.objects.filter(
        task__created_by=request.user
    ).count()
    
    # Get recent logs
    recent_logs = ActivityLog.objects.filter(
        task__created_by=request.user
    ).order_by('-timestamp')[:10]
    
    context = {
        'profile': profile,
        'recent_tasks': recent_tasks,
        'active_tasks': active_tasks,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'total_ids_created': total_ids_created,
        'recent_logs': recent_logs,
    }
    
    return render(request, 'bot_dashboard/dashboard.html', context)


@login_required
def settings_view(request):
    settings_list = BotSettings.objects.filter(created_by=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        form = BotSettingsForm(request.POST)
        if form.is_valid():
            setting = form.save(commit=False)
            setting.created_by = request.user
            setting.save()
            messages.success(request, 'Settings saved successfully!')
            return redirect('bot_dashboard:settings')
    else:
        form = BotSettingsForm()
    
    context = {
        'settings_list': settings_list,
        'form': form,
    }
    
    return render(request, 'bot_dashboard/settings.html', context)


@login_required
def tasks_view(request):
    tasks = BotTask.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        tasks = tasks.filter(
            Q(name__icontains=search_query) |
            Q(status__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'bot_dashboard/tasks.html', context)


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(BotTask, id=task_id, created_by=request.user)
    created_ids = task.created_ids.all().order_by('-created_at')
    logs = task.logs.all().order_by('-timestamp')
    
    context = {
        'task': task,
        'created_ids': created_ids,
        'logs': logs,
    }
    
    return render(request, 'bot_dashboard/task_detail.html', context)


@login_required
def create_task(request):
    if request.method == 'POST':
        form = BotTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            
            # Start the task
            if task.status == 'pending':
                start_bot_task.delay(task.id)
                task.status = 'running'
                task.started_at = timezone.now()
                task.save()
            
            messages.success(request, 'Task created and started successfully!')
            return redirect('bot_dashboard:task_detail', task_id=task.id)
    else:
        form = BotTaskForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'bot_dashboard/create_task.html', context)


@login_required
@require_POST
def start_task(request, task_id):
    task = get_object_or_404(BotTask, id=task_id, created_by=request.user)
    
    if task.status in ['pending', 'stopped', 'failed']:
        start_bot_task.delay(task.id)
        task.status = 'running'
        task.started_at = timezone.now()
        task.save()
        
        ActivityLog.objects.create(
            task=task,
            level='info',
            message='Task started by user'
        )
        
        return JsonResponse({'status': 'success', 'message': 'Task started successfully'})
    
    return JsonResponse({'status': 'error', 'message': 'Task cannot be started'})


@login_required
@require_POST
def stop_task(request, task_id):
    try:
        task = get_object_or_404(BotTask, id=task_id, created_by=request.user)
        
        if task.status == 'running':
            # First, update the task status immediately to prevent race conditions
            task.status = 'stopped'
            task.completed_at = timezone.now()
            task.save()
            
            # Stop all device sessions immediately
            sessions = DeviceSession.objects.filter(task=task, status='active')
            for session in sessions:
                session.status = 'stopped'
                session.ended_at = timezone.now()
                session.save()
                
                # Free up device
                device = session.device
                device.status = 'available'
                device.save()
            
            # Log the stop action
            ActivityLog.objects.create(
                task=task,
                level='warning',
                message='Task stopped by user'
            )
            
            # Try to stop the Celery task asynchronously
            try:
                stop_bot_task.delay(task.id)
            except Exception as e:
                # If Celery task fails, log it but don't fail the request
                ActivityLog.objects.create(
                    task=task,
                    level='error',
                    message=f'Failed to stop background task: {str(e)}'
                )
            
            return JsonResponse({'status': 'success', 'message': 'Task stopped successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Task cannot be stopped - not currently running'})
            
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error stopping task: {str(e)}'})


@login_required
def logs_view(request):
    logs = ActivityLog.objects.filter(task__created_by=request.user).order_by('-timestamp')
    
    # Filter by level
    level_filter = request.GET.get('level', '')
    if level_filter:
        logs = logs.filter(level=level_filter)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        logs = logs.filter(message__icontains=search_query)
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'level_filter': level_filter,
    }
    
    return render(request, 'bot_dashboard/logs.html', context)


@login_required
def download_ids(request, task_id):
    task = get_object_or_404(BotTask, id=task_id, created_by=request.user)
    created_ids = task.created_ids.all()
    
    # Create the file content
    content = f"Facebook IDs Created - Task: {task.name}\n"
    content += f"Created: {task.created_at}\n"
    content += f"Status: {task.status}\n"
    content += "=" * 50 + "\n\n"
    
    for fb_id in created_ids:
        content += f"Email: {fb_id.email}\n"
        content += f"Password: {fb_id.password}\n"
        content += f"Domain: {fb_id.domain}\n"
        content += f"Device: {fb_id.device_name}\n"
        content += f"Status: {fb_id.status}\n"
        content += "-" * 30 + "\n"
    
    from django.http import HttpResponse
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="fb_created_ids_{task_id}.txt"'
    return response


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_dashboard_stats(request):
    """Get dashboard statistics for AJAX requests"""
    profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    active_tasks = BotTask.objects.filter(
        created_by=request.user,
        status__in=['pending', 'running']
    ).count()
    
    total_ids_created = CreatedFacebookID.objects.filter(
        task__created_by=request.user
    ).count()
    
    recent_logs = ActivityLog.objects.filter(
        task__created_by=request.user
    ).order_by('-timestamp')[:5]
    
    return Response({
        'active_tasks': active_tasks,
        'total_ids_created': total_ids_created,
        'recent_logs': [
            {
                'level': log.level,
                'message': log.message,
                'timestamp': log.timestamp.isoformat(),
                'device_name': log.device_name
            }
            for log in recent_logs
        ]
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_task_status(request, task_id):
    """Get real-time task status"""
    try:
        task = BotTask.objects.get(id=task_id, created_by=request.user)
        return Response({
            'id': task.id,
            'name': task.name,
            'status': task.status,
            'progress': task.progress,
            'created_ids_count': task.created_ids_count,
            'failed_count': task.failed_count,
            'total_ids_to_create': task.total_ids_to_create,
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'duration': str(task.duration) if task.duration else None,
        })
    except BotTask.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND) 