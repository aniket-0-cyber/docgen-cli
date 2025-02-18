# docgen/generators/docstring_generator.py
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class DocstringTemplate:
    function_template: str = '''"""
    {description}

    Args:
        {args}

    Returns:
        {returns}
    """'''

    class_template: str = '''"""
    {description}

    Attributes:
        {attributes}

    Methods:
        {methods}
    """'''

class DocstringGenerator:
    def __init__(self, template_style: str = "google"):
        self.template = DocstringTemplate()
        self.template_style = template_style

    def generate_function_docstring(self, function_info: Dict) -> str:
        description = self._generate_description(function_info["name"])
        args_str = self._format_arguments(function_info["args"])
        returns_str = function_info.get("returns", "None")
        
        return self.template.function_template.format(
            description=description,
            args=args_str,
            returns=returns_str
        )

    def _generate_description(self, name: str) -> str:
        words = []
        current_word = ""
        
        for char in name:
            if char.isupper() and current_word:
                words.append(current_word)
                current_word = char
            elif char == "_":
                if current_word:
                    words.append(current_word)
                current_word = ""
            else:
                current_word += char
                
        if current_word:
            words.append(current_word)
            
        description = " ".join(word.lower() for word in words)
        return description.capitalize() + "."

    def _format_arguments(self, args: List[str]) -> str:
        if not args:
            return "None"
        return "\n        ".join(
            f"{arg}: Description for {arg}" for arg in args if arg != "self"
        )
