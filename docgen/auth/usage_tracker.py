import hashlib
import platform
import uuid
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from cryptography.fernet import Fernet
import base64
import os
import requests
from rich.console import Console
from .api_key_manager import APIKeyManager

console = Console()

class UsageTracker:
    def __init__(self):
        self.config_dir = Path.home() / '.docgen'
        self.usage_file = self.config_dir / 'usage.enc'
        self.config_dir.mkdir(exist_ok=True)
        
        # Plan limits
        self.plan_limits = {
            'anonymous': 20,
            'free': 50,
            'pro': 500
        }
        
        # Cache for API verification
        self._cache_file = self.config_dir / 'api_cache.json'
        self._cache_duration = timedelta(hours=1)
        
        # Generate machine ID if not exists
        self.machine_id = self._get_or_create_machine_id()
        
        # Initialize Fernet for encryption
        self.fernet = self._initialize_fernet()
        
        # Initialize usage file if it doesn't exist
        if not self.usage_file.exists():
            self._save_usage(self._get_initial_usage())

    def _get_initial_usage(self) -> dict:
        return {
            'anonymous_requests': [],
            'authenticated_requests': [],
            'api_key': None,
            'plan': 'anonymous',
            'machine_id': self.machine_id,
            'integrity_hash': ''
        }

    def _initialize_fernet(self) -> Fernet:
        """Set up encryption key or load existing one."""
        try:
            key_file = self.config_dir / '.key'
            if not key_file.exists():
                # Generate a new encryption key
                key = Fernet.generate_key()
                # Save the key in protected mode (600)
                key_file.write_bytes(key)
                os.chmod(key_file, 0o600)
            else:
                key = key_file.read_bytes()
            return Fernet(key)
        except Exception as e:
            console.print(f"[red]Error setting up encryption: {str(e)}[/red]")
            raise

    def _get_or_create_machine_id(self) -> str:
        """Generate a unique machine identifier with hardware info."""
        try:
            system_info = [
                platform.node(),
                platform.machine(),
                platform.processor(),
                str(uuid.getnode()),
                platform.system(),
                platform.version(),
                self._get_disk_id(),  # Add disk identifier
                self._get_cpu_info()   # Add CPU information
            ]
            
            machine_id = hashlib.sha256(''.join(system_info).encode()).hexdigest()
            return machine_id
        except:
            return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()

    def _get_disk_id(self) -> str:
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

    def _get_cpu_info(self) -> str:
        """Get CPU information based on OS."""
        try:
            if platform.system() == 'Windows':
                return platform.processor()
            else:
                # For Unix-based systems
                with open('/proc/cpuinfo', 'r') as f:
                    cpu_info = f.read()
                return hashlib.sha256(cpu_info.encode()).hexdigest()
        except:
            return platform.processor()

    def _get_cached_api_info(self, api_key: str) -> Optional[dict]:
        """Get cached API key info if valid."""
        try:
            if not self._cache_file.exists():
                return None
                
            cache_data = json.loads(self._cache_file.read_text())
            if (
                cache_data.get('api_key') == api_key and
                cache_data.get('timestamp') and
                datetime.fromisoformat(cache_data['timestamp']) + self._cache_duration > datetime.now()
            ):
                return cache_data
            return None
        except:
            return None

    def _cache_api_info(self, api_key: str, plan: str) -> None:
        """Cache API key info."""
        cache_data = {
            'api_key': api_key,
            'plan': plan,
            'timestamp': datetime.now().isoformat()
        }
        self._cache_file.write_text(json.dumps(cache_data))

    def _verify_api_key(self, api_key: str) -> Optional[str]:
        """Verify API key and return plan, using cache when possible."""
        # Check cache first
        cached_info = self._get_cached_api_info(api_key)
        if cached_info:
            return cached_info['plan']

        # If not in cache, verify with server
        try:
            response = requests.post(
                'http://localhost:8000/api/v1/auth/verify-key',
                json={'api_key': api_key},
                timeout=10  # Reduced timeout
            )
            if response.status_code == 200:
                plan = response.json()['key_info']['plan']
                self._cache_api_info(api_key, plan)
                return plan
        except:
            pass
        return None

    def _load_usage(self) -> dict:
        try:
            # Read and decrypt the data
            encrypted_data = self.usage_file.read_bytes()
            decrypted_data = self.fernet.decrypt(encrypted_data)
            data = json.loads(decrypted_data)
            
            # Get API key and plan from APIKeyManager
            api_key_manager = APIKeyManager()
            api_key = api_key_manager.get_api_key()
            plan = api_key_manager.get_plan()
            
            # Update data with current API key and plan
            data['api_key'] = api_key
            data['plan'] = plan if api_key and plan else 'anonymous'
                
            # Save updated data
            self._save_usage(data)
            return data
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load usage data: {str(e)}[/yellow]")
            return self._get_initial_usage()

    def _save_usage(self, usage: dict) -> None:
        """Save encrypted usage data."""
        try:
            usage['machine_id'] = self.machine_id
            usage['integrity_hash'] = self._calculate_integrity_hash(usage)
            
            # Encrypt and save the data
            encrypted_data = self.fernet.encrypt(json.dumps(usage).encode())
            self.usage_file.write_bytes(encrypted_data)
            os.chmod(self.usage_file, 0o600)  # Set file permissions to user read/write only
            
        except Exception as e:
            console.print(f"[red]Error saving usage data: {str(e)}[/red]")

    def _calculate_integrity_hash(self, data: Dict) -> str:
        """Calculate hash of usage data to detect tampering."""
        # Create a copy without the integrity_hash field
        data_copy = data.copy()
        data_copy.pop('integrity_hash', None)
        
        # Sort the dictionary to ensure consistent hashing
        data_str = json.dumps(data_copy, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def can_make_request(self) -> Tuple[bool, str]:
        """Check if a request can be made based on current usage."""
        usage_data = self._load_usage()
        current_month = datetime.now().strftime('%Y-%m')
        
        if usage_data.get('api_key'):
            # Authenticated requests
            monthly_requests = [r for r in usage_data['authenticated_requests'] 
                              if r.startswith(current_month)]
            limit = self.plan_limits[usage_data['plan'].lower()]  # Convert to lowercase
            count = len(monthly_requests)
            return count < limit, f"Authenticated requests: {count}/{limit}"
        else:
            # Anonymous requests
            monthly_requests = [r for r in usage_data['anonymous_requests'] 
                              if r.startswith(current_month)]
            limit = self.plan_limits['anonymous']
            count = len(monthly_requests)
            return count < limit, f"Anonymous requests: {count}/{limit}"

    def track_request(self) -> None:
        """Track a new request."""
        usage_data = self._load_usage()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if usage_data.get('api_key'):
            usage_data['authenticated_requests'].append(timestamp)
        else:
            usage_data['anonymous_requests'].append(timestamp)
            
        self._save_usage(usage_data)