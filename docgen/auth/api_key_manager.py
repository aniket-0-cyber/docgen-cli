import json
from pathlib import Path
import uuid
import requests
from typing import Optional

class APIKeyManager:
    def __init__(self):
        self.config_dir = Path.home() / '.docgen'
        self.config_file = self.config_dir / 'auth.json'
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize config file if it doesn't exist
        if not self.config_file.exists():
            self._save_config({'api_key': None})

    def _load_config(self) -> dict:
        try:
            return json.loads(self.config_file.read_text())
        except:
            return {'api_key': None}

    def _save_config(self, config: dict) -> None:
        self.config_file.write_text(json.dumps(config, indent=2))

    def get_api_key(self) -> Optional[str]:
        """Get the stored API key."""
        config = self._load_config()
        return config.get('api_key')

    def set_api_key(self, api_key: str) -> None:
        """Store the API key."""
        config = self._load_config()
        config['api_key'] = api_key
        self._save_config(config)

    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key with your server."""
        try:
            response = requests.post(
                'https://your-api-server.com/validate-key',
                json={'api_key': api_key}
            )
            return response.status_code == 200
        except:
            return False 