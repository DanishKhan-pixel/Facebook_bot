from django import forms
from .models import Device, EmulatorProfile


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = [
            'name', 'device_type', 'device_id', 'platform', 'version',
            'screen_resolution', 'ip_address', 'port', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Device Name'
            }),
            'device_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'device_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ADB Device ID'
            }),
            'platform': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Android'
            }),
            'version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Android Version'
            }),
            'screen_resolution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1080x1920'
            }),
            'ip_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '192.168.1.100'
            }),
            'port': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 65535
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes about this device'
            }),
        }

    def clean_device_id(self):
        device_id = self.cleaned_data['device_id']
        if not device_id:
            raise forms.ValidationError('Device ID is required')
        return device_id


class EmulatorProfileForm(forms.ModelForm):
    class Meta:
        model = EmulatorProfile
        fields = [
            'name', 'emulator_path', 'android_version', 'screen_resolution',
            'ram_size', 'cpu_count'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Profile Name'
            }),
            'emulator_path': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '/path/to/memu/console.exe'
            }),
            'android_version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '7.1'
            }),
            'screen_resolution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1080x1920'
            }),
            'ram_size': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '2048MB'
            }),
            'cpu_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 8
            }),
        }

    def clean_emulator_path(self):
        emulator_path = self.cleaned_data['emulator_path']
        if not emulator_path:
            raise forms.ValidationError('Emulator path is required')
        return emulator_path 