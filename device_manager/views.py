from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import subprocess
import json
import re

from .models import Device, DeviceSession, DeviceLog, EmulatorProfile
from .forms import DeviceForm, EmulatorProfileForm
from .utils import detect_devices, check_device_status


@login_required
def device_list(request):
    devices = Device.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        devices = devices.filter(
            Q(name__icontains=search_query) |
            Q(device_id__icontains=search_query) |
            Q(status__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        devices = devices.filter(status=status_filter)
    
    # Filter by type
    type_filter = request.GET.get('type', '')
    if type_filter:
        devices = devices.filter(device_type=type_filter)
    
    # Pagination
    paginator = Paginator(devices, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
    }
    
    return render(request, 'device_manager/device_list.html', context)


@login_required
def device_detail(request, device_id):
    device = get_object_or_404(Device, id=device_id, created_by=request.user)
    sessions = device.sessions.all().order_by('-started_at')
    logs = device.logs.all().order_by('-timestamp')
    
    context = {
        'device': device,
        'sessions': sessions,
        'logs': logs,
    }
    
    return render(request, 'device_manager/device_detail.html', context)


@login_required
def add_device(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.created_by = request.user
            
            # Check if device is online
            if device.ip_address:
                device.status = 'available'
            else:
                device.status = 'offline'
            
            device.save()
            
            DeviceLog.objects.create(
                device=device,
                level='info',
                message=f'Device {device.name} added successfully',
                action='device_added'
            )
            
            messages.success(request, 'Device added successfully!')
            return redirect('device_detail', device_id=device.id)
    else:
        form = DeviceForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'device_manager/add_device.html', context)


@login_required
@require_POST
def scan_devices(request):
    """Scan for connected devices using ADB"""
    try:
        # Run ADB devices command
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            devices_found = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) == 2:
                        device_id, status = parts
                        devices_found.append({
                            'device_id': device_id,
                            'status': status,
                            'name': f"Device {device_id[:8]}",
                            'device_type': 'physical' if 'emulator' not in device_id else 'emulator'
                        })
            
            # Update existing devices or create new ones
            for device_info in devices_found:
                device, created = Device.objects.get_or_create(
                    device_id=device_info['device_id'],
                    created_by=request.user,
                    defaults={
                        'name': device_info['name'],
                        'device_type': device_info['device_type'],
                        'status': 'available' if device_info['status'] == 'device' else 'offline'
                    }
                )
                
                if not created:
                    # Update status of existing device
                    device.status = 'available' if device_info['status'] == 'device' else 'offline'
                    device.save()
                
                DeviceLog.objects.create(
                    device=device,
                    level='info',
                    message=f'Device scanned - Status: {device_info["status"]}',
                    action='device_scanned'
                )
            
            return JsonResponse({
                'status': 'success',
                'message': f'Found {len(devices_found)} devices',
                'devices': devices_found
            })
        
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'ADB command failed'
            })
    
    except subprocess.TimeoutExpired:
        return JsonResponse({
            'status': 'error',
            'message': 'ADB command timed out'
        })
    except FileNotFoundError:
        return JsonResponse({
            'status': 'error',
            'message': 'ADB not found. Please install Android SDK.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error scanning devices: {str(e)}'
        })


@login_required
@require_POST
def check_device_status(request, device_id):
    """Check if a specific device is online"""
    device = get_object_or_404(Device, id=device_id, created_by=request.user)
    
    try:
        # Run ADB command to check device
        result = subprocess.run(
            ['adb', '-s', device.device_id, 'shell', 'echo', 'test'],
            capture_output=True, text=True, timeout=5
        )
        
        if result.returncode == 0:
            device.status = 'available'
            device.save()
            
            DeviceLog.objects.create(
                device=device,
                level='info',
                message='Device is online and responsive',
                action='status_check'
            )
            
            return JsonResponse({
                'status': 'success',
                'device_status': 'available',
                'message': 'Device is online'
            })
        else:
            device.status = 'offline'
            device.save()
            
            DeviceLog.objects.create(
                device=device,
                level='warning',
                message='Device is offline or not responding',
                action='status_check'
            )
            
            return JsonResponse({
                'status': 'success',
                'device_status': 'offline',
                'message': 'Device is offline'
            })
    
    except Exception as e:
        device.status = 'error'
        device.save()
        
        DeviceLog.objects.create(
            device=device,
            level='error',
            message=f'Error checking device status: {str(e)}',
            action='status_check'
        )
        
        return JsonResponse({
            'status': 'error',
            'message': f'Error checking device: {str(e)}'
        })


@login_required
def emulator_profiles(request):
    profiles = EmulatorProfile.objects.filter(created_by=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        form = EmulatorProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.created_by = request.user
            profile.save()
            messages.success(request, 'Emulator profile created successfully!')
            return redirect('emulator_profiles')
    else:
        form = EmulatorProfileForm()
    
    context = {
        'profiles': profiles,
        'form': form,
    }
    
    return render(request, 'device_manager/emulator_profiles.html', context)


@login_required
@require_POST
def start_emulator(request, profile_id):
    """Start MEmu emulator with specified profile"""
    profile = get_object_or_404(EmulatorProfile, id=profile_id, created_by=request.user)
    
    try:
        # Start MEmu emulator
        cmd = [
            profile.emulator_path,
            'launch', '--index', '0'  # Adjust based on MEmu CLI
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Create device record for the emulator
            device, created = Device.objects.get_or_create(
                device_id=f"emulator-{profile.id}",
                created_by=request.user,
                defaults={
                    'name': f"MEmu {profile.name}",
                    'device_type': 'emulator',
                    'status': 'available',
                    'platform': 'Android',
                    'version': profile.android_version,
                    'screen_resolution': profile.screen_resolution,
                }
            )
            
            DeviceLog.objects.create(
                device=device,
                level='info',
                message=f'Emulator {profile.name} started successfully',
                action='emulator_started'
            )
            
            return JsonResponse({
                'status': 'success',
                'message': f'Emulator {profile.name} started successfully'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to start emulator: {result.stderr}'
            })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error starting emulator: {str(e)}'
        })


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_device_status(request):
    """Get real-time device status"""
    devices = Device.objects.filter(created_by=request.user)
    
    return Response({
        'devices': [
            {
                'id': device.id,
                'name': device.name,
                'device_id': device.device_id,
                'status': device.status,
                'device_type': device.device_type,
                'is_online': device.is_online,
                'last_seen': device.last_seen.isoformat(),
            }
            for device in devices
        ]
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_device_sessions(request, device_id):
    """Get device sessions"""
    device = get_object_or_404(Device, id=device_id, created_by=request.user)
    sessions = device.sessions.all().order_by('-started_at')
    
    return Response({
        'sessions': [
            {
                'id': session.id,
                'task_name': session.task.name,
                'started_at': session.started_at.isoformat(),
                'status': session.status,
                'created_ids_count': session.created_ids_count,
                'failed_count': session.failed_count,
                'duration': str(session.duration) if session.duration else None,
            }
            for session in sessions
        ]
    }) 