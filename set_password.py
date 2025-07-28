import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facebook_bot.settings')
django.setup()

from django.contrib.auth.models import User

# Get the user and set password
user = User.objects.get(username='danish')
user.set_password('password123')
user.save()

print("Password set successfully!")
print("Username: danish")
print("Password: password123") 