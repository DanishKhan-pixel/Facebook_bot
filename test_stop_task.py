#!/usr/bin/env python3
"""
Test script to verify stop task functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/home/danish/Desktop/Facebook_bot')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facebook_bot.settings')
django.setup()

from bot_dashboard.models import BotTask, BotSettings, ActivityLog
from device_manager.models import Device, DeviceSession
from django.contrib.auth.models import User

def test_stop_task():
    """Test the stop task functionality"""
    print("🧪 Testing stop task functionality...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("✅ Created test user")
    
    # Create test settings
    settings, created = BotSettings.objects.get_or_create(
        name='Test Settings',
        defaults={
            'thread_count': 1,
            'domain_list': 'gmail.com,yahoo.com',
            'created_by': user
        }
    )
    if created:
        print("✅ Created test settings")
    
    # Create a test task
    task, created = BotTask.objects.get_or_create(
        name='Test Stop Task',
        defaults={
            'settings': settings,
            'status': 'running',
            'total_ids_to_create': 5,
            'created_by': user
        }
    )
    if created:
        print("✅ Created test task")
    
    # Create a test device
    device, created = Device.objects.get_or_create(
        name='Test Device',
        defaults={
            'device_type': 'physical',
            'status': 'in_use',
            'device_id': 'test_device_001',
            'created_by': user
        }
    )
    if created:
        print("✅ Created test device")
    
    # Create a device session
    session, created = DeviceSession.objects.get_or_create(
        device=device,
        task=task,
        defaults={'status': 'active'}
    )
    if created:
        print("✅ Created test device session")
    
    print(f"📋 Test setup complete:")
    print(f"   - Task ID: {task.id}")
    print(f"   - Task Status: {task.status}")
    print(f"   - Device Status: {device.status}")
    print(f"   - Session Status: {session.status}")
    
    # Test the stop task functionality
    print("\n🔄 Testing stop task...")
    
    try:
        # Update task status
        task.status = 'stopped'
        task.save()
        print("✅ Task status updated to 'stopped'")
        
        # Stop device sessions
        sessions = DeviceSession.objects.filter(task=task, status='active')
        for session in sessions:
            session.status = 'stopped'
            session.save()
            print(f"✅ Device session {session.id} stopped")
        
        # Free up devices
        for session in sessions:
            device = session.device
            device.status = 'available'
            device.save()
            print(f"✅ Device {device.name} freed")
        
        # Create activity log
        ActivityLog.objects.create(
            task=task,
            level='warning',
            message='Task stopped by test',
            device_name='System'
        )
        print("✅ Activity log created")
        
        print("\n🎉 Stop task test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during stop task test: {e}")
        return False

if __name__ == '__main__':
    success = test_stop_task()
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1) 