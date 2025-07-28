#!/usr/bin/env python3
"""
Simple run script for Facebook ID Creator Bot
Starts the Django development server with proper configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check if virtual environment exists
    if not Path("venv").exists():
        print("❌ Virtual environment not found. Please run setup.py first.")
        return False
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("⚠️  .env file not found. Creating basic configuration...")
        with open(".env", "w") as f:
            f.write("SECRET_KEY=django-insecure-development-key\n")
            f.write("DEBUG=True\n")
            f.write("ALLOWED_HOSTS=localhost,127.0.0.1\n")
            f.write("REDIS_URL=redis://localhost:6379/0\n")
    
    # Check if database exists
    if not Path("db.sqlite3").exists():
        print("⚠️  Database not found. Running migrations...")
        python_cmd = "venv/bin/python" if os.name != "nt" else "venv\\Scripts\\python"
        subprocess.run([python_cmd, "manage.py", "migrate"], check=True)
    
    print("✅ Requirements check completed")
    return True

def start_redis():
    """Start Redis server if not running"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running")
        return True
    except:
        print("⚠️  Redis is not running")
        print("Please start Redis server in another terminal:")
        print("  redis-server")
        return False

def start_celery():
    """Start Celery worker"""
    print("🔄 Starting Celery worker...")
    python_cmd = "venv/bin/python" if os.name != "nt" else "venv\\Scripts\\python"
    
    try:
        # Start Celery worker in background
        if os.name == "nt":  # Windows
            subprocess.Popen([
                python_cmd, "-m", "celery", "-A", "facebook_bot.celery", "worker", 
                "--loglevel=info", "--pool=solo"
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Unix/Linux
            subprocess.Popen([
                python_cmd, "-m", "celery", "-A", "facebook_bot.celery", "worker", 
                "--loglevel=info"
            ])
        print("✅ Celery worker started")
        return True
    except Exception as e:
        print(f"❌ Failed to start Celery worker: {e}")
        return False

def start_server():
    """Start Django development server"""
    print("🚀 Starting Django development server...")
    python_cmd = "venv/bin/python" if os.name != "nt" else "venv\\Scripts\\python"
    
    try:
        subprocess.run([
            python_cmd, "manage.py", "runserver", "0.0.0.0:8000"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

def main():
    """Main function"""
    print("🚀 Facebook ID Creator Bot")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check Redis
    if not start_redis():
        print("⚠️  Continuing without Redis (some features may not work)")
    
    # Start Celery
    start_celery()
    
    print("\n" + "=" * 40)
    print("🌐 Starting web server...")
    print("📱 Access the application at: http://localhost:8000")
    print("🔧 Admin panel: http://localhost:8000/admin")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 40)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main() 