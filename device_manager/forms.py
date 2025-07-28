from django import forms
from .models import Device, EmulatorProfile


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = [
            'name', 'device_type', 'platform', 'connection_type', 
            'connection_details', 'is_emulator', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Device Name',
                'required': True
            }),
            'device_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'platform': forms.Select(choices=[
                ('android', 'Android'),
                ('ios', 'iOS'),
                ('desktop', 'Desktop')
            ], attrs={
                'class': 'form-control',
                'required': True
            }),
            'connection_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'connection_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'IP address, port, or other connection information'
            }),
            'is_emulator': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_device_id(self):
        device_id = self.cleaned_data.get('device_id')
        if not device_id:
            # Generate a device ID if not provided
            import uuid
            device_id = f"device_{uuid.uuid4().hex[:8]}"
        return device_id

    def save(self, commit=True):
        device = super().save(commit=False)
        if not device.device_id:
            import uuid
            device.device_id = f"device_{uuid.uuid4().hex[:8]}"
        if commit:
            device.save()
        return device


class EmulatorProfileForm(forms.ModelForm):
    class Meta:
        model = EmulatorProfile
        fields = [
            'name', 'platform', 'device_model', 'resolution', 
            'api_level', 'android_version', 'ios_version'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Profile Name'
            }),
            'platform': forms.Select(choices=[
                ('android', 'Android'),
                ('ios', 'iOS')
            ], attrs={
                'class': 'form-control'
            }),
            'device_model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Device Model'
            }),
            'resolution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1080x1920'
            }),
            'api_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 16,
                'max': 34
            }),
            'android_version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '11.0'
            }),
            'ios_version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '15.0'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make platform-dependent fields optional
        self.fields['api_level'].required = False
        self.fields['android_version'].required = False
        self.fields['ios_version'].required = False 