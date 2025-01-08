# docgen/config/language_config.py
from typing import Dict, Any
from pathlib import Path
import json

DEFAULT_CONFIGS = {
    "python": {
        "docstring_style": "google",
        "indent": 4,
        "max_line_length": 88,
        "templates": {
            "function": """\"\"\"
    {description}

    Args:
        {args}

    Returns:
        {returns}
    \"\"\"""",
            "class": """\"\"\"
    {description}

    Attributes:
        {attributes}

    Methods:
        {methods}
    \"\"\""""
        }
    },
    "javascript": {
        "docstring_style": "jsdoc",
        "indent": 2,
        "max_line_length": 80,
        "templates": {
            "function": """/**
 * {description}
 *
 * @param {type} {param} - {param_description}
 * @returns {type} {returns_description}
 */""",
            "class": """/**
 * {description}
 *
 * @class
 * @property {type} {property} - {property_description}
 */"""
        }
    },
    "java": {
        "docstring_style": "javadoc",
        "indent": 4,
        "max_line_length": 100,
        "templates": {
            "function": """/**
 * {description}
 *
 * @param {param} {param_description}
 * @return {returns_description}
 */""",
            "class": """/**
 * {description}
 *
 * @author {author}
 * @version {version}
 */"""
        }
    }
}

class LanguageConfig:
    def __init__(self):
        self.configs = DEFAULT_CONFIGS.copy()
        self._load_custom_configs()

    def _load_custom_configs(self):
        """
        Load custom language configurations from user's config directory.
        """
        config_dir = Path.home() / '.docgen' / 'language_configs'
        if config_dir.exists():
            for config_file in config_dir.glob('*.json'):
                language = config_file.stem
                try:
                    custom_config = json.loads(config_file.read_text())
                    if language in self.configs:
                        # Merge with default config
                        self.configs[language].update(custom_config)
                    else:
                        # Add new language config
                        self.configs[language] = custom_config
                except Exception as e:
                    print(f"Error loading custom config for {language}: {e}")

    def get_config(self, language: str) -> Dict[str, Any]:
        """
        Get configuration for specific language.
        """
        return self.configs.get(language, {})

    def add_language(self, language: str, config: Dict[str, Any]):
        """
        Add configuration for new language.
        """
        self.configs[language] = config
        self._save_custom_config(language, config)

    def _save_custom_config(self, language: str, config: Dict[str, Any]):
        """
        Save custom language configuration.
        """
        config_dir = Path.home() / '.docgen' / 'language_configs'
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = config_dir / f"{language}.json"
        config_file.write_text(json.dumps(config, indent=2))

    def get_supported_languages(self) -> list[str]:
        """
        Get list of supported languages.
        """
        return list(self.configs.keys())

# Example usage:
if __name__ == "__main__":
    # Initialize language configuration
    lang_config = LanguageConfig()
    
    # Get configuration for Python
    python_config = lang_config.get_config("python")
    print(f"Python docstring style: {python_config['docstring_style']}")
    
    # Add configuration for a new language
    rust_config = {
        "docstring_style": "rustdoc",
        "indent": 4,
        "max_line_length": 100,
        "templates": {
            "function": "/// {description}\n///\n/// # Arguments\n///\n/// * `{param}` - {param_description}\n///\n/// # Returns\n///\n/// * `{returns_description}`",
            "class": "/// {description}\n///\n/// # Fields\n///\n/// * `{field}` - {field_description}"
        }
    }
    lang_config.add_language("rust", rust_config)