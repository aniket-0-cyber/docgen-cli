# docgen/config/config_handler.py
from pathlib import Path
import json
from typing import Any

DEFAULT_CONFIG = {
    "template_style": "google",
    "output_format": "markdown",
    "recursive": False,
    "exclude_patterns": ["**/venv/**", "**/__pycache__/**", "**/tests/**"],
    "docstring_style": {
        "function_template": '''"""
    {description}

    Args:
        {args}

    Returns:
        {returns}
    """''',
        "class_template": '''"""
    {description}

    Attributes:
        {attributes}

    Methods:
        {methods}
    """'''
    },
    "ai_settings": {
        "enabled": True,
        "model": "gemini-1.5-flash-8b",
        "temperature": 0.7,
        "max_tokens": 2048,
        "prompt_template": "custom"  # or "default"
    }
}

VALID_TEMPLATE_STYLES = ["google", "numpy", "sphinx"]
VALID_OUTPUT_FORMATS = ["markdown", "html"]

class ConfigHandler:
    def __init__(self):
        self.app_dir = Path.home() / ".docgen"
        self.config_path = self.app_dir / "config.json"
        self._config = {
            "template_style": "google",
            "output_format": "markdown",
            "recursive": False
        }
        self.load()
    
    def load(self):
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    self._config.update(json.load(f))
            except json.JSONDecodeError:
                pass
    
    def get(self, key, default=None):
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value with validation."""
        if key == "template_style" and value not in VALID_TEMPLATE_STYLES:
            raise ValueError(f"Invalid template style. Must be one of: {VALID_TEMPLATE_STYLES}")
        elif key == "output_format" and value not in VALID_OUTPUT_FORMATS:
            raise ValueError(f"Invalid output format. Must be one of: {VALID_OUTPUT_FORMATS}")
        elif key == "recursive" and not isinstance(value, bool):
            value = str(value).lower() == "true"
        
        self._config[key] = value
    
    def save(self):
        self.app_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self._config, f, indent=2)
