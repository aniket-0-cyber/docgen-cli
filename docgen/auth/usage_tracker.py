import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Tuple
from rich.console import Console

console = Console()
class UsageTracker:
    def __init__(self):
        self.config_dir = Path.home() / '.docgen'
        self.usage_file = self.config_dir / 'usage.json'
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize usage file if it doesn't exist
        if not self.usage_file.exists():
            self._save_usage({
                'anonymous_requests': [],
                'authenticated_requests': [],
                'api_key': None,
                'plan': 'anonymous'
            })

    def _load_usage(self) -> dict:
        try:
            return json.loads(self.usage_file.read_text())
        except:
            return {'anonymous_requests': [], 'authenticated_requests': [], 'api_key': None, 'plan': 'anonymous'}

    def _save_usage(self, usage: dict) -> None:
        self.usage_file.write_text(json.dumps(usage, indent=2))

    def _get_monthly_limit(self) -> int:
        """Get monthly request limit based on plan."""
        limits = {
            'anonymous': 11,    # Free usage without API key
            'free': 25,        # Free tier with API key
            'pro': 500,
            'enterprise': float('inf')
        }
        usage = self._load_usage()
        return limits.get(usage.get('plan', 'anonymous'), 20)

    def _clean_old_requests(self, requests: list) -> list:
        """Remove requests older than 30 days."""
        thirty_days_ago = datetime.now() - timedelta(days=30)
        return [r for r in requests if datetime.fromisoformat(r['timestamp']) > thirty_days_ago]

    def can_make_request(self) -> Tuple[bool, str]:
        """Check if user can make more requests this month.
        Returns (can_make_request, message)"""
        usage = self._load_usage()
        api_key = usage.get('api_key')
        
        if api_key:
            # Authenticated user
            requests = self._clean_old_requests(usage['authenticated_requests'])
            limit = self._get_monthly_limit()
            can_request = len(requests) < limit
            message = f"Authenticated requests: {len(requests)}/{limit}"
        else:
            # Anonymous user
            requests = self._clean_old_requests(usage['anonymous_requests'])
            limit = self._get_monthly_limit()
            can_request = len(requests) < limit
            remaining = limit - len(requests)
            
            if remaining <= 5:
                message = f"⚠️  Only {remaining} anonymous requests remaining. Login to increase your limit!"
            else:
                message = f"Anonymous requests: {len(requests)}/{limit}"
        
        return can_request, message

    def track_request(self) -> None:
        """Track a new request."""
        try:
            usage = self._load_usage()
            api_key = usage.get('api_key')
            
            request_data = {
                'timestamp': datetime.now().isoformat(),
                'type': 'documentation'
            }
            
            if api_key:
                requests = self._clean_old_requests(usage['authenticated_requests'])
                requests.append(request_data)
                usage['authenticated_requests'] = requests
            else:
                requests = self._clean_old_requests(usage['anonymous_requests'])
                requests.append(request_data)
                usage['anonymous_requests'] = requests
                
            self._save_usage(usage)
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to track request: {str(e)}[/yellow]") 