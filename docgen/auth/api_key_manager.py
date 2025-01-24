import json
from pathlib import Path
import uuid
import requests
from typing import Optional, Tuple
from datetime import datetime

class APIKeyManager:
    def __init__(self):
        self.config_dir = Path.home() / '.docgen'
        self.config_file = self.config_dir / 'auth.json'
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize config file if it doesn't exist
        if not self.config_file.exists():
            self._save_config({'api_key': None, 'plan': None, 'verified_at': None})

    def _load_config(self) -> dict:
        try:
            return json.loads(self.config_file.read_text())
        except:
            return {'api_key': None, 'plan': None, 'verified_at': None}

    def _save_config(self, config: dict) -> None:
        self.config_file.write_text(json.dumps(config, indent=2))

    def get_api_key(self) -> Optional[str]:
        """Get the stored API key."""
        config = self._load_config()
        return config.get('api_key')

    def get_plan(self) -> Optional[str]:
        """Get the stored plan."""
        config = self._load_config()
        return config.get('plan')

    def set_api_key(self, api_key: Optional[str], plan: Optional[str] = None) -> None:
        """Store the API key and plan."""
        config = self._load_config()
        config['api_key'] = api_key
        config['plan'] = plan
        config['verified_at'] = datetime.utcnow().isoformat() if api_key else None
        self._save_config(config)

    def validate_api_key(self, api_key: str) -> Tuple[bool, Optional[str]]:
        """Validate API key with server and return (success, plan)."""
        try:
            response = requests.post(
                'http://localhost:8000/api/v1/auth/verify-key',
                json={'api_key': api_key},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                plan = data['key_info'].get('plan', 'free')  # Default to free if not specified
                self.set_api_key(api_key, plan)
                return True, plan
            self.set_api_key(None, None)  # Clear invalid key
            return False, None
        except Exception as e:
            print(f"Error validating API key: {str(e)}")
            return False, None 