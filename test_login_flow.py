#!/usr/bin/env python3
"""
Test script to verify login flow and URL routing
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/home/danish/Desktop/Facebook_bot')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facebook_bot.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

def test_login_flow():
    """Test the login flow and URL routing"""
    print("🧪 Testing login flow and URL routing...")
    
    client = Client()
    
    # Test 1: Root URL redirects to login
    print("\n1. Testing root URL redirect...")
    response = client.get('/')
    print(f"   Root URL (/) -> Status: {response.status_code}")
    if response.status_code == 302:
        print(f"   Redirects to: {response.url}")
    else:
        print("   ❌ Root URL should redirect to login")
        return False
    
    # Test 2: Swagger URL redirects to login
    print("\n2. Testing swagger URL redirect...")
    response = client.get('/swagger/')
    print(f"   Swagger URL (/swagger/) -> Status: {response.status_code}")
    if response.status_code == 302:
        print(f"   Redirects to: {response.url}")
    else:
        print("   ❌ Swagger URL should redirect to login")
        return False
    
    # Test 3: Login page is accessible
    print("\n3. Testing login page accessibility...")
    response = client.get('/dashboard/login/')
    print(f"   Login page -> Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Login page is accessible")
    else:
        print("   ❌ Login page should be accessible")
        return False
    
    # Test 4: Create a test user
    print("\n4. Creating test user...")
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("   ✅ Test user created")
    else:
        print("   ℹ️ Test user already exists")
    
    # Test 5: Login with test user
    print("\n5. Testing login with test user...")
    login_success = client.login(username='testuser', password='testpass123')
    if login_success:
        print("   ✅ Login successful")
    else:
        print("   ❌ Login failed")
        return False
    
    # Test 6: Dashboard is accessible after login
    print("\n6. Testing dashboard access after login...")
    response = client.get('/dashboard/')
    print(f"   Dashboard -> Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Dashboard is accessible after login")
    else:
        print("   ❌ Dashboard should be accessible after login")
        return False
    
    # Test 7: Logout
    print("\n7. Testing logout...")
    response = client.get('/dashboard/logout/')
    print(f"   Logout -> Status: {response.status_code}")
    if response.status_code == 302:
        print("   ✅ Logout successful")
    else:
        print("   ❌ Logout should redirect")
        return False
    
    print("\n🎉 All login flow tests passed!")
    return True

if __name__ == '__main__':
    success = test_login_flow()
    if success:
        print("\n✅ Login flow is working correctly!")
    else:
        print("\n❌ Login flow has issues!")
        sys.exit(1) 