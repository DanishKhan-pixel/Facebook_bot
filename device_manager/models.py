from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class Device(models.Model):
    DEVICE_TYPES = [
        ('physical', 'Physical Device'),
        ('emulator', 'MEmu Emulator'),
        ('virtual', 'Virtual Device'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('offline', 'Offline'),
        ('error', 'Error'),
    ]

    CONNECTION_TYPES = [
        ('usb', 'USB'),
        ('wifi', 'WiFi'),
        ('bluetooth', 'Bluetooth'),
    ]

    name = models.CharField(max_length=200)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    device_id = models.CharField(max_length=200, unique=True)  # ADB device ID
    platform = models.CharField(max_length=50, default='Android')
    version = models.CharField(max_length=50, blank=True)
    screen_resolution = models.CharField(max_length=50, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    port = models.IntegerField(default=5555)
    is_active = models.BooleanField(default=True)
    is_emulator = models.BooleanField(default=False)
    connection_type = models.CharField(max_length=20, choices=CONNECTION_TYPES, default='usb')
    connection_details = models.TextField(blank=True)
    is_connected = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.device_id})"

    @property
    def is_online(self):
        return self.status in ['available', 'in_use']

    @property
    def adb_connection_string(self):
        if self.ip_address:
            return f"{self.ip_address}:{self.port}"
        return self.device_id


class DeviceSession(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='sessions')
    task = models.ForeignKey('bot_dashboard.BotTask', on_delete=models.CASCADE, related_name='device_sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='active')
    created_ids_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    current_email = models.EmailField(blank=True)
    current_domain = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.device.name} - {self.task.name}"

    @property
    def duration(self):
        if self.ended_at:
            return self.ended_at - self.started_at
        return timezone.now() - self.started_at


class DeviceLog(models.Model):
    LOG_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('debug', 'Debug'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='logs')
    session = models.ForeignKey(DeviceSession, on_delete=models.CASCADE, related_name='logs', null=True, blank=True)
    level = models.CharField(max_length=20, choices=LOG_LEVELS, default='info')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100, blank=True)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.device.name} - {self.level.upper()}: {self.message[:50]}"


class EmulatorProfile(models.Model):
    name = models.CharField(max_length=200)
    platform = models.CharField(max_length=20, choices=[
        ('android', 'Android'),
        ('ios', 'iOS')
    ], default='android')
    device_model = models.CharField(max_length=100, blank=True)
    resolution = models.CharField(max_length=50, blank=True)
    api_level = models.IntegerField(null=True, blank=True)
    android_version = models.CharField(max_length=50, blank=True)
    ios_version = models.CharField(max_length=50, blank=True)
    emulator_path = models.CharField(max_length=500, blank=True)
    ram_size = models.CharField(max_length=20, blank=True)
    cpu_count = models.IntegerField(default=2)
    is_active = models.BooleanField(default=True)
    is_running = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name 