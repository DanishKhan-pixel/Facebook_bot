# Facebook ID Creator Bot - Web Application

A comprehensive Django web application for automated Facebook ID creation with device management, real-time monitoring, and multi-threaded task processing.

## 🚀 Features

### Core Features
- **User Dashboard**: Modern web interface with authentication and user management
- **Device Management**: Detect and control physical phones and MEmu emulators
- **ID Creation Interface**: Start, stop, and monitor Facebook ID creation from web
- **Custom Settings**: Configure passwords, domains, threading, and other options
- **Auto OTP Handling**: Integrate with TempMail API for automatic OTP handling
- **Multi-threaded Task Engine**: Backend system for parallel bot/device processing
- **Activity Logs & Reports**: Real-time logs, error handling, and downloadable reports
- **Downloadable Output**: Generated IDs saved in downloadable files
- **Admin Panel**: Manage users, roles, access, and bot limits

### Technical Features
- **Real-time Updates**: WebSocket integration for live task progress
- **Device Detection**: ADB integration for automatic device discovery
- **Task Management**: Create, monitor, and control bot tasks
- **Settings Management**: Customizable bot configurations
- **Log Management**: Comprehensive logging system
- **File Downloads**: Export created IDs in text format

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Redis Server
- Android SDK (for ADB)
- MEmu Emulator (optional)

### Setup Instructions

1. **Clone the repository**
```bash
git clone <repository-url>
cd facebook_bot
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp env_example.txt .env
# Edit .env with your configuration
```

5. **Run database migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Start Redis server**
```bash
redis-server
```

8. **Start Celery worker**
```bash
celery -A facebook_bot.celery worker --loglevel=info
```

9. **Run the development server**
```bash
python manage.py runserver
```

## 📁 Project Structure

```
facebook_bot/
├── facebook_bot/          # Main Django project
│   ├── settings.py        # Django settings
│   ├── urls.py           # Main URL configuration
│   ├── asgi.py           # ASGI configuration
│   ├── wsgi.py           # WSGI configuration
│   └── celery.py         # Celery configuration
├── bot_dashboard/         # Main dashboard app
│   ├── models.py         # User profiles, tasks, settings
│   ├── views.py          # Dashboard views
│   ├── forms.py          # Forms for task creation
│   └── consumers.py      # WebSocket consumers
├── device_manager/        # Device management app
│   ├── models.py         # Device models
│   ├── views.py          # Device management views
│   ├── utils.py          # ADB utilities
│   └── forms.py          # Device forms
├── task_engine/          # Task processing app
│   ├── tasks.py          # Celery tasks
│   └── models.py         # Task models
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   └── bot_dashboard/    # Dashboard templates
├── static/              # Static files
├── media/               # User uploaded files
├── requirements.txt      # Python dependencies
└── manage.py            # Django management
```

## 🔧 Configuration

### Environment Variables (.env)
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
REDIS_URL=redis://localhost:6379/0
TEMP_MAIL_API_KEY=your-tempmail-api-key
```

### Database Configuration
The application uses SQLite by default. For production, configure PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'facebook_bot',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🚀 Usage

### 1. Login
- Access the application at `http://localhost:8000`
- Login with your superuser credentials

### 2. Device Management
- Go to "Devices" section
- Click "Scan Devices" to detect connected devices
- Add devices manually or scan automatically
- Configure MEmu emulator profiles

### 3. Bot Settings
- Go to "Settings" section
- Create bot configurations with:
  - Password templates
  - Domain lists
  - Thread counts
  - Delay settings
  - TempMail API integration

### 4. Task Creation
- Go to "Tasks" section
- Click "Create Task"
- Select settings and specify number of IDs to create
- Start the task

### 5. Monitoring
- View real-time progress on dashboard
- Monitor device status and logs
- Download created IDs

## 🔌 API Endpoints

### Dashboard API
- `GET /api/dashboard/stats/` - Get dashboard statistics
- `GET /api/tasks/{id}/status/` - Get task status

### Device API
- `GET /api/devices/status/` - Get device status
- `GET /api/devices/{id}/sessions/` - Get device sessions

## 🛡️ Security Features

- **Authentication**: Django's built-in authentication system
- **CSRF Protection**: Cross-site request forgery protection
- **Session Management**: Secure session handling
- **Input Validation**: Form validation and sanitization
- **SQL Injection Protection**: Django ORM protection

## 📊 Monitoring & Logging

### Activity Logs
- Task creation and completion
- Device status changes
- Error tracking
- User actions

### System Logs
- Application errors
- Performance metrics
- Security events

## 🔧 Development

### Running Tests
```bash
python manage.py test
```

### Code Style
```bash
# Install pre-commit hooks
pre-commit install
```

### Database Reset
```bash
python manage.py flush
python manage.py loaddata initial_data.json
```

## 🚀 Deployment

### Production Setup
1. Set `DEBUG=False` in settings
2. Configure production database
3. Set up static file serving
4. Configure WebSocket support
5. Set up Celery with Redis
6. Configure logging

### Docker Deployment
```bash
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This application is for educational and research purposes only. Users are responsible for complying with Facebook's Terms of Service and applicable laws.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the logs for error details

## 🔄 Updates

### Version 1.0.0
- Initial release with core features
- Device management
- Task processing
- Real-time monitoring
- Web interface

### Planned Features
- Advanced device automation
- Multiple platform support
- Enhanced reporting
- Mobile app companion # Facebook_bot
