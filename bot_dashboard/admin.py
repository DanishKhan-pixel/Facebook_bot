from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    UserProfile, BotSettings, BotTask, CreatedFacebookID, 
    ActivityLog, SystemLog
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_admin', 'max_devices', 'max_threads', 'created_at']
    list_filter = ['is_admin', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BotSettings)
class BotSettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'thread_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'use_temp_mail', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'created_by')
        }),
        ('Bot Configuration', {
            'fields': ('password_template', 'domain_list', 'thread_count', 'delay_between_actions')
        }),
        ('Email Settings', {
            'fields': ('use_temp_mail', 'temp_mail_api_key')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BotTask)
class BotTaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'status', 'progress', 'created_ids_count', 'created_at']
    list_filter = ['status', 'created_at', 'settings']
    search_fields = ['name', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'started_at', 'completed_at', 'task_id']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'created_by', 'settings')
        }),
        ('Task Configuration', {
            'fields': ('total_ids_to_create', 'status')
        }),
        ('Progress', {
            'fields': ('progress', 'created_ids_count', 'failed_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
        ('Technical', {
            'fields': ('task_id',),
            'classes': ('collapse',)
        }),
    )


@admin.register(CreatedFacebookID)
class CreatedFacebookIDAdmin(admin.ModelAdmin):
    list_display = ['email', 'domain', 'device_name', 'status', 'created_at']
    list_filter = ['status', 'domain', 'created_at']
    search_fields = ['email', 'device_name', 'task__name']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Facebook ID Information', {
            'fields': ('task', 'email', 'password', 'domain')
        }),
        ('Device Information', {
            'fields': ('device_name', 'status')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at')
        }),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['task', 'level', 'device_name', 'timestamp']
    list_filter = ['level', 'timestamp', 'device_name']
    search_fields = ['message', 'task__name', 'device_name']
    readonly_fields = ['timestamp']
    fieldsets = (
        ('Log Information', {
            'fields': ('task', 'level', 'message')
        }),
        ('Device Information', {
            'fields': ('device_name',)
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['level', 'message', 'user', 'timestamp']
    list_filter = ['level', 'timestamp']
    search_fields = ['message', 'user__username']
    readonly_fields = ['timestamp']
    fieldsets = (
        ('Log Information', {
            'fields': ('level', 'message')
        }),
        ('User Information', {
            'fields': ('user',)
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )


# Customize User admin to include UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Customize admin site
admin.site.site_header = "Facebook ID Creator Bot Admin"
admin.site.site_title = "Facebook Bot Admin"
admin.site.index_title = "Welcome to Facebook Bot Administration" 