from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import BotSettings, BotTask


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class BotSettingsForm(forms.ModelForm):
    class Meta:
        model = BotSettings
        fields = [
            'name', 'description', 'password_template', 'domain_list',
            'thread_count', 'delay_between_actions', 'use_temp_mail',
            'temp_mail_api_key'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Settings Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description (optional)'
            }),
            'password_template': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Password123!'
            }),
            'domain_list': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'facebook.com\ninstagram.com\n...'
            }),
            'thread_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
            'delay_between_actions': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
            'temp_mail_api_key': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'TempMail API Key (optional)'
            }),
        }

    def clean_domain_list(self):
        domain_list = self.cleaned_data['domain_list']
        # Convert to list if it's a string with multiple lines
        if isinstance(domain_list, str):
            domains = [domain.strip() for domain in domain_list.split('\n') if domain.strip()]
            return '\n'.join(domains)
        return domain_list


class BotTaskForm(forms.ModelForm):
    class Meta:
        model = BotTask
        fields = ['name', 'settings', 'total_ids_to_create', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Task Name'
            }),
            'settings': forms.Select(attrs={
                'class': 'form-control'
            }),
            'total_ids_to_create': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 1000,
                'placeholder': 'Number of IDs to create'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['settings'].queryset = BotSettings.objects.filter(
                created_by=user,
                is_active=True
            ) 