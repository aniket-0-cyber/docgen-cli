# docgen/utils/config.py
from pathlib import Path
import json
from typing import Dict, Optional
import typer

DEFAULT_CONFIG = {
    "template_style": "google",
    "output_format": "markdown",
    "recursive": False,
    "exclude_patterns": ["**/venv/**", "**/__pycache__/**", "**/tests/**"],
    "docstring_style": {
        "function_template": """\"\"\"
    {description}

    Args:
        {args}

    Returns:
        {returns}
    \"\"\"""",
        "class_template": """\"\"\"
    {description}

    Attributes:
        {attributes}

    Methods:
        {methods}
    \"\"\""""
    }
}

class ConfigHandler:
    def __init__(self):
        self.app_dir = typer.get_app_dir("docgen")
        self.config_path = Path(self.app_dir) / "config.json"
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """
        Load configuration from file or create default if it doesn't exist.
        """
        try:
            if self.config_path.exists():
                return json.loads(self.config_path.read_text())
            else:
                return self._create_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._create_default_config()

    def _create_default_config(self) -> Dict:
        """
        Create and save default configuration.
        """
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(DEFAULT_CONFIG, indent=4))
        return DEFAULT_CONFIG.copy()

    def get(self, key: str, default: Optional[any] = None) -> any:
        """
        Get a configuration value.
        """
        return self.config.get(key, default)

    def set(self, key: str, value: any) -> None:
        """
        Set a configuration value and save to file.
        """
        self.config[key] = value
        self._save_config()

    def _save_config(self) -> None:
        """
        Save current configuration to file.
        """
        try:
            self.config_path.write_text(json.dumps(self.config, indent=4))
        except Exception as e:
            print(f"Error saving config: {e}")

    def update(self, new_config: Dict) -> None:
        """
        Update multiple configuration values at once.
        """
        self.config.update(new_config)
        self._save_config()

    def reset(self) -> None:
        """
        Reset configuration to defaults.
        """
        self.config = DEFAULT_CONFIG.copy()
        self._save_config()

    @property
    def template_style(self) -> str:
        return self.get("template_style", "google")

    @property
    def output_format(self) -> str:
        return self.get("output_format", "markdown")

    @property
    def recursive(self) -> bool:
        return self.get("recursive", False)

    @property
    def exclude_patterns(self) -> list:
        return self.get("exclude_patterns", [])

    @property
    def docstring_templates(self) -> Dict:
        return self.get("docstring_style", {})

if __name__ == "__main__":
    # Example usage
    config = ConfigHandler()
    print(f"Current template style: {config.template_style}")
    
    # Update a setting
    config.set("template_style", "numpy")
    
    # Update multiple settings
    config.update({
        "output_format": "html",
        "recursive": True
    })
    
    # Reset to defaults
    config.reset()