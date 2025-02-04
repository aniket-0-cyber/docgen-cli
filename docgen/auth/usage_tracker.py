import requests
from typing import Dict, Tuple, Optional
from rich.console import Console
from .api_key_manager import APIKeyManager
from ..utils.machine_utils import get_machine_id
from docgen.config.urls import URLConfig
from typing import Tuple

console = Console()

class UsageTracker:
    def __init__(self):
        self.machine_id = get_machine_id()
        self.api_key_manager = APIKeyManager()
        
        # Base URL for API calls
        self.base_url = URLConfig.USAGE_BASE_URL


    def can_make_request(self) -> Tuple[bool, str]:
        """Check if a request can be made based on current usage."""
        try:
            headers = {
                'x-machine-id': self.machine_id,
                'x-api-key': self.api_key_manager.get_api_key()
            }
            
            response = requests.get(
                f"{self.base_url}/check",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                can_request = data['remaining'] > 0
                message = f"{data['plan'].title()} requests: {data['current_usage']}/{data['limit']}"
                return can_request, message
            else:
                return False, "Error checking usage limits"
                
        except Exception as e:
            console.print(f"[yellow]Warning: Could not check usage limits: {str(e)}[/yellow]")
            return False, "Error checking usage limits"

    def track_request(self) -> None:
        """Track a new request."""
        try:
            headers = {
                'x-machine-id': self.machine_id,
                'x-api-key': self.api_key_manager.get_api_key()
            }
            
            response = requests.post(
                f"{self.base_url}/track",
                headers=headers,
                json={'request_type': 'doc_generation'},  # Send as JSON body
                timeout=10
            )
            
            if response.status_code != 200:
                console.print("[yellow]Warning: Failed to track request[/yellow]")
                
        except Exception as e:
            console.print(f"[yellow]Warning: Could not track request: {str(e)}[/yellow]")