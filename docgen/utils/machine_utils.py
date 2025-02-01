import hashlib
import platform
import uuid

def get_machine_id() -> str:
    """Generate a unique machine identifier with hardware info."""
    try:
        system_info = [
            platform.node(),
            platform.machine(),
            platform.processor(),
            str(uuid.getnode()),
            platform.system(),
            platform.version(),
            _get_disk_id(),
            _get_cpu_info()
        ]
        
        machine_id = hashlib.sha256(''.join(system_info).encode()).hexdigest()
        return machine_id
    except:
        return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()

def _get_disk_id() -> str:
    """Get disk identifier based on OS."""
    try:
        if platform.system() == 'Windows':
            import win32api
            drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]
            return hashlib.sha256(str(drives[0]).encode()).hexdigest()
        else:
            # For Unix-based systems
            with open('/etc/machine-id', 'r') as f:
                return f.read().strip()
    except:
        return ""

def _get_cpu_info() -> str:
    """Get CPU information based on OS."""
    try:
        if platform.system() == 'Windows':
            return platform.processor()
        else:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('model name'):
                        return line.split(':')[1].strip()
        return platform.processor()
    except:
        return platform.processor() 