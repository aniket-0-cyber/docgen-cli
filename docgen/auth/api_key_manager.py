import json
from pathlib import Path
import requests
from typing import Optional, Tuple
from ..utils.machine_utils import get_machine_id
from docgen.config.urls import URLConfig

class APIKeyManager:
    def __init__(self):
        self.config_dir = Path.home() / '.docgen'
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / 'config.json'
        self.machine_id = get_machine_id()
        
        # Initialize config file if it doesn't exist
        if not self.config_file.exists():
            self._save_config({'api_key': None})
    
    def _save_config(self, config: dict) -> None:
        """Save configuration to file."""
        self.config_file.write_text(json.dumps(config))
    
    def _load_config(self) -> dict:
        """Load configuration from file."""
        try:
            return json.loads(self.config_file.read_text())
        except:
            return {'api_key': None}
    
    def get_api_key(self) -> Optional[str]:
        """Get stored API key."""
        return self._load_config().get('api_key')
    
    def set_api_key(self, api_key: Optional[str]) -> None:
        """Store API key."""
        config = self._load_config()
        config['api_key'] = api_key
        self._save_config(config)
    
    def validate_api_key(self, api_key: str) -> Tuple[bool, Optional[str]]:
        """Validate API key with server and return (success, plan)."""
        try:
            response = requests.post(
                f"{URLConfig.AUTH_BASE_URL}/verify-key",
                json={'api_key': api_key, 'machine_id': self.machine_id},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                plan = data['key_info'].get('plan', 'free')
                self.set_api_key(api_key)
                return True, plan
            self.set_api_key(None)  # Clear invalid key
            return False, None
        except Exception as e:
            print(f"Error validating API key: {str(e)}")
            return False, None 