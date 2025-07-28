import subprocess
import re
import time
from typing import List, Dict, Optional


def detect_devices() -> List[Dict]:
    """
    Detect connected devices using ADB
    Returns list of device dictionaries
    """
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            return []
        
        devices = []
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        
        for line in lines:
            if line.strip():
                parts = line.split('\t')
                if len(parts) == 2:
                    device_id, status = parts
                    device_info = {
                        'device_id': device_id,
                        'status': status,
                        'name': f"Device {device_id[:8]}",
                        'device_type': 'physical' if 'emulator' not in device_id else 'emulator',
                        'is_online': status == 'device'
                    }
                    devices.append(device_info)
        
        return devices
    
    except Exception as e:
        print(f"Error detecting devices: {e}")
        return []


def check_device_status(device_id: str) -> Dict:
    """
    Check if a specific device is online and responsive
    Returns device status dictionary
    """
    try:
        # Test device connectivity
        result = subprocess.run(
            ['adb', '-s', device_id, 'shell', 'echo', 'test'],
            capture_output=True, text=True, timeout=5
        )
        
        if result.returncode == 0:
            # Get device info
            info_result = subprocess.run(
                ['adb', '-s', device_id, 'shell', 'getprop'],
                capture_output=True, text=True, timeout=10
            )
            
            device_info = {
                'device_id': device_id,
                'status': 'online',
                'is_online': True,
                'error': None
            }
            
            if info_result.returncode == 0:
                # Parse device properties
                props = info_result.stdout
                device_info.update({
                    'model': _extract_property(props, 'ro.product.model'),
                    'brand': _extract_property(props, 'ro.product.brand'),
                    'android_version': _extract_property(props, 'ro.build.version.release'),
                    'sdk_version': _extract_property(props, 'ro.build.version.sdk'),
                })
            
            return device_info
        else:
            return {
                'device_id': device_id,
                'status': 'offline',
                'is_online': False,
                'error': 'Device not responding'
            }
    
    except subprocess.TimeoutExpired:
        return {
            'device_id': device_id,
            'status': 'timeout',
            'is_online': False,
            'error': 'Connection timeout'
        }
    except Exception as e:
        return {
            'device_id': device_id,
            'status': 'error',
            'is_online': False,
            'error': str(e)
        }


def _extract_property(props: str, property_name: str) -> Optional[str]:
    """Extract property value from getprop output"""
    pattern = rf'\[{property_name}\]:\s*\[([^\]]*)\]'
    match = re.search(pattern, props)
    return match.group(1) if match else None


def install_app_on_device(device_id: str, apk_path: str) -> Dict:
    """
    Install APK on device
    Returns installation result
    """
    try:
        result = subprocess.run(
            ['adb', '-s', device_id, 'install', '-r', apk_path],
            capture_output=True, text=True, timeout=60
        )
        
        if result.returncode == 0:
            return {
                'success': True,
                'message': 'App installed successfully',
                'output': result.stdout
            }
        else:
            return {
                'success': False,
                'message': 'App installation failed',
                'error': result.stderr
            }
    
    except Exception as e:
        return {
            'success': False,
            'message': 'Installation error',
            'error': str(e)
        }


def uninstall_app_from_device(device_id: str, package_name: str) -> Dict:
    """
    Uninstall app from device
    Returns uninstallation result
    """
    try:
        result = subprocess.run(
            ['adb', '-s', device_id, 'uninstall', package_name],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            return {
                'success': True,
                'message': 'App uninstalled successfully',
                'output': result.stdout
            }
        else:
            return {
                'success': False,
                'message': 'App uninstallation failed',
                'error': result.stderr
            }
    
    except Exception as e:
        return {
            'success': False,
            'message': 'Uninstallation error',
            'error': str(e)
        }


def get_device_screen_resolution(device_id: str) -> Optional[str]:
    """Get device screen resolution"""
    try:
        result = subprocess.run(
            ['adb', '-s', device_id, 'shell', 'wm', 'size'],
            capture_output=True, text=True, timeout=5
        )
        
        if result.returncode == 0:
            # Parse output like "Physical size: 1080x1920"
            match = re.search(r'(\d+x\d+)', result.stdout)
            return match.group(1) if match else None
        
        return None
    
    except Exception:
        return None


def take_screenshot(device_id: str, output_path: str) -> Dict:
    """
    Take screenshot from device
    Returns screenshot result
    """
    try:
        # Take screenshot on device
        result = subprocess.run(
            ['adb', '-s', device_id, 'shell', 'screencap', '/sdcard/screenshot.png'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            # Pull screenshot to local machine
            pull_result = subprocess.run(
                ['adb', '-s', device_id, 'pull', '/sdcard/screenshot.png', output_path],
                capture_output=True, text=True, timeout=10
            )
            
            if pull_result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Screenshot taken successfully',
                    'path': output_path
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to pull screenshot',
                    'error': pull_result.stderr
                }
        else:
            return {
                'success': False,
                'message': 'Failed to take screenshot',
                'error': result.stderr
            }
    
    except Exception as e:
        return {
            'success': False,
            'message': 'Screenshot error',
            'error': str(e)
        }


def connect_to_device(ip_address: str, port: int = 5555) -> Dict:
    """
    Connect to device via TCP/IP
    Returns connection result
    """
    try:
        result = subprocess.run(
            ['adb', 'connect', f'{ip_address}:{port}'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            return {
                'success': True,
                'message': f'Connected to {ip_address}:{port}',
                'output': result.stdout
            }
        else:
            return {
                'success': False,
                'message': 'Connection failed',
                'error': result.stderr
            }
    
    except Exception as e:
        return {
            'success': False,
            'message': 'Connection error',
            'error': str(e)
        } 