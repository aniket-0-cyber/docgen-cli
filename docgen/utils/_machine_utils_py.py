"""
Pure Python implementation of machine_utils for platforms where Cython compilation fails.
This is used as a fallback on Windows systems without a C++ compiler.
"""

import hashlib
import platform
import uuid
import os
import subprocess

def get_machine_id() -> str:
    """Generate a unique machine identifier with hardware info."""
    # First try to get from cache file
    cached_id = _get_cached_machine_id()
    if cached_id:
        return cached_id
        
    # Generate new ID if no cache exists
    try:
        system_info = _get_stable_system_info()
        machine_id = hashlib.sha256(''.join(system_info).encode()).hexdigest()
        _save_machine_id(machine_id)
        return machine_id
    except:
        # Fallback to MAC-based ID
        fallback_id = hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()
        _save_machine_id(fallback_id)
        return fallback_id

def _get_stable_system_info():
    """Get stable system information across platforms."""
    info = []
    
    # MAC address (generally stable)
    info.append(str(uuid.getnode()))
    
    # OS-specific hardware identifiers
    if platform.system() == 'Windows':
        info.extend(_get_windows_info())
    elif platform.system() == 'Darwin':  # macOS
        info.extend(_get_macos_info())
    else:  # Linux and other Unix-like
        info.extend(_get_linux_info())
        
    return info

def _get_windows_info():
    """Get stable Windows-specific identifiers."""
    try:
        info = []
        
        # Try to get volume serial number
        try:
            import ctypes
            volume_serial = ctypes.c_ulong()
            ctypes.windll.kernel32.GetVolumeInformationW(
                u"C:\\", None, 0, ctypes.byref(volume_serial), None, None, None, 0
            )
            info.append(str(volume_serial.value))
        except:
            pass
            
        # Try to get computer name
        try:
            import socket
            info.append(socket.gethostname())
        except:
            pass
            
        return info
    except:
        return []

def _get_macos_info():
    """Get stable macOS-specific identifiers."""
    try:
        info = []
        
        # Hardware UUID
        try:
            result = subprocess.run(['system_profiler', 'SPHardwareDataType'], 
                                 capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'Hardware UUID' in line:
                    info.append(line.split(':')[1].strip())
                elif 'Serial Number' in line:
                    info.append(line.split(':')[1].strip())
        except:
            pass
            
        return info
    except:
        return []

def _get_linux_info():
    """Get stable Linux-specific identifiers."""
    try:
        info = []
        
        # Try machine-id files
        for path in ['/etc/machine-id', '/var/lib/dbus/machine-id']:
            try:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        content = f.read().strip()
                        if content:
                            info.append(content)
            except:
                pass
                
        # Try DMI system information
        try:
            for path in ['/sys/class/dmi/id/product_uuid', 
                        '/sys/class/dmi/id/board_serial']:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        content = f.read().strip()
                        if content and content != '0000000000':
                            info.append(content)
        except:
            pass
            
        return info
    except:
        return []

def _get_cached_machine_id():
    """Get machine ID from cache file."""
    try:
        cache_dir = os.path.expanduser('~/.docgen/cache')
        cache_file = os.path.join(cache_dir, '.machine_id')
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return f.read().strip()
    except:
        pass
    return ""

def _save_machine_id(machine_id):
    """Save machine ID to cache file."""
    try:
        cache_dir = os.path.expanduser('~/.docgen/cache')
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, '.machine_id')
        
        with open(cache_file, 'w') as f:
            f.write(machine_id)
    except:
        pass 