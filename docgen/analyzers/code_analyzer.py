from pathlib import Path
from typing import Dict, Any
from .base_analyzer import BaseAnalyzer

class CodeAnalyzer(BaseAnalyzer):
    def __init__(self, path: Path):
        """Initialize the analyzer with a file path."""
        if not isinstance(path, Path):
            path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")
        
        self.path = path
        self.source = ""
        
    def analyze_file(self) -> Dict[str, Any]:
        """
        Analyzes any source code file for AI documentation generation.
        Returns basic file information and content.
        """
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                self.source = f.read()
            
            return {
                "file_path": str(self.path),
                "file_name": self.path.name,
                "extension": self.path.suffix,
                "source_code": self.source,
                "size": len(self.source)
            }
        except Exception as e:
            raise Exception(f"Error analyzing file {self.path}: {str(e)}")
