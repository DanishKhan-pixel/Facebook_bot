from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    max_devices = models.IntegerField(default=5)
    max_threads = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class BotSettings(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    password_template = models.CharField(max_length=200, default="Password123!")
    domain_list = models.TextField(default="facebook.com")  # JSON field for multiple domains
    thread_count = models.IntegerField(default=1)
    delay_between_actions = models.IntegerField(default=2)  # seconds
    use_temp_mail = models.BooleanField(default=True)
    temp_mail_api_key = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_domain_list(self):
        try:
            return json.loads(self.domain_list)
        except:
            return [self.domain_list]

    def set_domain_list(self, domains):
        if isinstance(domains, list):
            self.domain_list = json.dumps(domains)
        else:
            self.domain_list = domains

    def __str__(self):
        return self.name


class BotTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('stopped', 'Stopped'),
    ]

    name = models.CharField(max_length=200)
    settings = models.ForeignKey(BotSettings, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0)  # 0-100
    total_ids_to_create = models.IntegerField(default=1)
    created_ids_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    task_id = models.CharField(max_length=255, blank=True)  # Celery task ID

    def __str__(self):
        return f"{self.name} - {self.status}"

    @property
    def duration(self):
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return timezone.now() - self.started_at
        return None


class CreatedFacebookID(models.Model):
    task = models.ForeignKey(BotTask, on_delete=models.CASCADE, related_name='created_ids')
    email = models.EmailField()
    password = models.CharField(max_length=200)
    domain = models.CharField(max_length=100)
    device_name = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=50, default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.email} - {self.domain}"


class ActivityLog(models.Model):
    LOG_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('success', 'Success'),
    ]

    task = models.ForeignKey(BotTask, on_delete=models.CASCADE, related_name='logs')
    level = models.CharField(max_length=20, choices=LOG_LEVELS, default='info')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    device_name = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.level.upper()}: {self.message[:50]}"


class SystemLog(models.Model):
    LOG_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('debug', 'Debug'),
    ]

    level = models.CharField(max_length=20, choices=LOG_LEVELS, default='info')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.level.upper()}: {self.message[:50]}" 