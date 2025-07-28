#!/usr/bin/env python3
"""
Setup script for Facebook ID Creator Bot
Automates the installation and configuration process
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def create_virtual_environment():
    """Create virtual environment"""
    if not os.path.exists("venv"):
        return run_command("python -m venv venv", "Creating virtual environment")
    else:
        print("✅ Virtual environment already exists")
        return True

def install_dependencies():
    """Install Python dependencies"""
    pip_cmd = "venv/bin/pip" if os.name != "nt" else "venv\\Scripts\\pip"
    return run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies")

def create_env_file():
    """Create .env file from example"""
    if not os.path.exists(".env"):
        if os.path.exists("env_example.txt"):
            shutil.copy("env_example.txt", ".env")
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your configuration")
        else:
            print("⚠️  No env_example.txt found, creating basic .env")
            with open(".env", "w") as f:
                f.write("SECRET_KEY=django-insecure-setup-key-change-this\n")
                f.write("DEBUG=True\n")
                f.write("ALLOWED_HOSTS=localhost,127.0.0.1\n")
                f.write("REDIS_URL=redis://localhost:6379/0\n")
    else:
        print("✅ .env file already exists")

def run_django_commands():
    """Run Django setup commands"""
    python_cmd = "venv/bin/python" if os.name != "nt" else "venv\\Scripts\\python"
    
    commands = [
        ("makemigrations", "Creating database migrations"),
        ("migrate", "Applying database migrations"),
        ("collectstatic --noinput", "Collecting static files"),
    ]
    
    for command, description in commands:
        if not run_command(f"{python_cmd} manage.py {command}", description):
            return False
    return True

def create_superuser():
    """Create Django superuser"""
    python_cmd = "venv/bin/python" if os.name != "nt" else "venv\\Scripts\\python"
    print("🔄 Creating superuser...")
    print("Please enter the following information:")
    return run_command(f"{python_cmd} manage.py createsuperuser", "Creating superuser")

def check_redis():
    """Check if Redis is running"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running")
        return True
    except:
        print("⚠️  Redis is not running")
        print("Please start Redis server: redis-server")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["logs", "media", "staticfiles"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("✅ Created necessary directories")

def main():
    """Main setup function"""
    print("🚀 Facebook ID Creator Bot Setup")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    if not create_virtual_environment():
        print("❌ Failed to create virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Create directories
    create_directories()
    
    # Run Django commands
    if not run_django_commands():
        print("❌ Failed to run Django commands")
        sys.exit(1)
    
    # Check Redis
    check_redis()
    
    # Create superuser
    create_superuser()
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your configuration")
    print("2. Start Redis server: redis-server")
    print("3. Start Celery worker: celery -A facebook_bot.celery worker --loglevel=info")
    print("4. Run the server: python manage.py runserver")
    print("5. Access the application at http://localhost:8000")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main() 