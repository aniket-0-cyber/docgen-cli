from typing import Optional
import requests
from docgen.auth.api_key_manager import APIKeyManager

class AIClient:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_key_manager = APIKeyManager()

    def generate_text(self, code: str, changes: Optional[str] = None, prompt_type: str = 'doc') -> Optional[str]:
        """Generate text using AI through the proxy server."""
        try:
            # Get API key if available, otherwise use anonymous
            api_key = self.api_key_manager.get_api_key()
            
            response = requests.post(
                f"{self.base_url}/api/v1/gemini/generate",
                json={
                    "code": code,
                    "changes": changes,
                    "prompt_type": prompt_type,
                    "api_key": api_key  # Can be None for anonymous
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json()["text"]
            elif response.status_code == 401:
                raise ValueError("Rate limit exceeded. Please login with an API key to increase your limit.")
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                raise ValueError(f"Error: {error_detail}")

        except Exception as e:
            print(f"Error generating text: {str(e)}")
            return None 