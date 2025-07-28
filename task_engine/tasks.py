import os
import time
import random
import string
import requests
from celery import shared_task
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

from bot_dashboard.models import BotTask, BotSettings, CreatedFacebookID, ActivityLog
from device_manager.models import Device, DeviceSession


@shared_task
def start_bot_task(task_id):
    """Start Facebook ID creation task"""
    try:
        task = BotTask.objects.get(id=task_id)
        task.status = 'running'
        task.started_at = timezone.now()
        task.save()
        
        # Log task start
        ActivityLog.objects.create(
            task=task,
            level='info',
            message='Task started successfully',
            device_name='System'
        )
        
        # Get available devices
        available_devices = Device.objects.filter(
            status='available',
            is_active=True
        )
        
        if not available_devices.exists():
            ActivityLog.objects.create(
                task=task,
                level='error',
                message='No available devices found',
                device_name='System'
            )
            task.status = 'failed'
            task.save()
            return
        
        # Get task settings
        settings = task.settings
        domains = settings.get_domain_list()
        
        # Calculate devices needed
        devices_needed = min(len(available_devices), settings.thread_count)
        selected_devices = available_devices[:devices_needed]
        
        # Create device sessions
        device_sessions = []
        for device in selected_devices:
            device.status = 'in_use'
            device.save()
            
            session = DeviceSession.objects.create(
                device=device,
                task=task
            )
            device_sessions.append(session)
            
            ActivityLog.objects.create(
                task=task,
                level='info',
                message=f'Device {device.name} assigned to task',
                device_name=device.name
            )
        
        # Start ID creation for each device
        for i, session in enumerate(device_sessions):
            create_facebook_id.delay(session.id, task_id, domains)
        
        # Update task progress
        task.progress = 10
        task.save()
        
        # Send WebSocket update
        send_task_update(task_id, 'running', 10, 0, 0)
        
    except BotTask.DoesNotExist:
        print(f"Task {task_id} not found")
    except Exception as e:
        print(f"Error starting task {task_id}: {e}")
        try:
            task = BotTask.objects.get(id=task_id)
            task.status = 'failed'
            task.save()
            
            ActivityLog.objects.create(
                task=task,
                level='error',
                message=f'Task failed to start: {str(e)}',
                device_name='System'
            )
        except:
            pass


@shared_task
def create_facebook_id(session_id, task_id, domains):
    """Create Facebook ID on a specific device"""
    try:
        session = DeviceSession.objects.get(id=session_id)
        task = BotTask.objects.get(id=task_id)
        device = session.device
        
        ActivityLog.objects.create(
            task=task,
            level='info',
            message=f'Starting Facebook ID creation on {device.name}',
            device_name=device.name
        )
        
        # Generate email using TempMail API
        email = generate_temp_email()
        if not email:
            ActivityLog.objects.create(
                task=task,
                level='error',
                message='Failed to generate temporary email',
                device_name=device.name
            )
            return
        
        # Select random domain
        domain = random.choice(domains) if domains else 'facebook.com'
        
        # Generate password
        password = generate_password()
        
        # Update session with current email
        session.current_email = email
        session.current_domain = domain
        session.save()
        
        ActivityLog.objects.create(
            task=task,
            level='info',
            message=f'Generated email: {email} for domain: {domain}',
            device_name=device.name
        )
        
        # Simulate Facebook account creation process
        success = simulate_facebook_creation(device, email, password, domain)
        
        if success:
            # Create Facebook ID record
            CreatedFacebookID.objects.create(
                task=task,
                email=email,
                password=password,
                domain=domain,
                device_name=device.name,
                status='created'
            )
            
            session.created_ids_count += 1
            session.save()
            
            task.created_ids_count += 1
            task.progress = min(100, int((task.created_ids_count / task.total_ids_to_create) * 100))
            task.save()
            
            ActivityLog.objects.create(
                task=task,
                level='success',
                message=f'Successfully created Facebook ID: {email}',
                device_name=device.name
            )
            
            # Send WebSocket update
            send_task_update(task_id, 'running', task.progress, task.created_ids_count, task.failed_count)
            
        else:
            session.failed_count += 1
            session.save()
            
            task.failed_count += 1
            task.save()
            
            ActivityLog.objects.create(
                task=task,
                level='error',
                message=f'Failed to create Facebook ID: {email}',
                device_name=device.name
            )
        
        # Check if task is complete
        if task.created_ids_count + task.failed_count >= task.total_ids_to_create:
            complete_task(task_id)
        
    except Exception as e:
        print(f"Error creating Facebook ID: {e}")
        try:
            session = DeviceSession.objects.get(id=session_id)
            session.failed_count += 1
            session.save()
            
            task = BotTask.objects.get(id=task_id)
            task.failed_count += 1
            task.save()
            
            ActivityLog.objects.create(
                task=task,
                level='error',
                message=f'Error in Facebook ID creation: {str(e)}',
                device_name=device.name if 'device' in locals() else 'Unknown'
            )
        except:
            pass


@shared_task
def stop_bot_task(task_id):
    """Stop Facebook ID creation task"""
    try:
        task = BotTask.objects.get(id=task_id)
        task.status = 'stopped'
        task.completed_at = timezone.now()
        task.save()
        
        # Stop all device sessions
        sessions = DeviceSession.objects.filter(task=task, status='active')
        for session in sessions:
            session.status = 'stopped'
            session.ended_at = timezone.now()
            session.save()
            
            # Free up device
            device = session.device
            device.status = 'available'
            device.save()
        
        ActivityLog.objects.create(
            task=task,
            level='warning',
            message='Task stopped by user',
            device_name='System'
        )
        
        # Send WebSocket update
        send_task_update(task_id, 'stopped', task.progress, task.created_ids_count, task.failed_count)
        
    except BotTask.DoesNotExist:
        print(f"Task {task_id} not found")
    except Exception as e:
        print(f"Error stopping task {task_id}: {e}")


def complete_task(task_id):
    """Mark task as completed"""
    try:
        task = BotTask.objects.get(id=task_id)
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.progress = 100
        task.save()
        
        # Free up all devices
        sessions = DeviceSession.objects.filter(task=task, status='active')
        for session in sessions:
            session.status = 'completed'
            session.ended_at = timezone.now()
            session.save()
            
            device = session.device
            device.status = 'available'
            device.save()
        
        ActivityLog.objects.create(
            task=task,
            level='success',
            message=f'Task completed successfully. Created {task.created_ids_count} IDs',
            device_name='System'
        )
        
        # Send WebSocket update
        send_task_update(task_id, 'completed', 100, task.created_ids_count, task.failed_count)
        
    except Exception as e:
        print(f"Error completing task {task_id}: {e}")


def generate_temp_email():
    """Generate temporary email using TempMail API"""
    try:
        # This is a placeholder - you would integrate with actual TempMail API
        # For now, we'll generate a random email
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        domain = random.choice(['tempmail.org', 'temp-mail.org', '10minutemail.com'])
        return f"{username}@{domain}"
    except Exception as e:
        print(f"Error generating temp email: {e}")
        return None


def generate_password():
    """Generate random password"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choices(chars, k=12))


def simulate_facebook_creation(device, email, password, domain):
    """Simulate Facebook account creation process"""
    try:
        # This is a placeholder for the actual Facebook automation
        # In a real implementation, you would use Selenium or similar
        
        # Simulate some processing time
        time.sleep(random.uniform(2, 5))
        
        # Simulate success/failure (90% success rate for demo)
        return random.random() < 0.9
        
    except Exception as e:
        print(f"Error in Facebook creation simulation: {e}")
        return False


def send_task_update(task_id, status, progress, created_count, failed_count):
    """Send task update via WebSocket"""
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'task_{task_id}',
            {
                'type': 'task_update',
                'task_id': task_id,
                'status': status,
                'progress': progress,
                'created_count': created_count,
                'failed_count': failed_count,
            }
        )
    except Exception as e:
        print(f"Error sending WebSocket update: {e}")


def send_log_message(task_id, level, message, device_name):
    """Send log message via WebSocket"""
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'task_{task_id}',
            {
                'type': 'log_message',
                'level': level,
                'message': message,
                'timestamp': timezone.now().isoformat(),
                'device_name': device_name,
            }
        )
    except Exception as e:
        print(f"Error sending log message: {e}") 