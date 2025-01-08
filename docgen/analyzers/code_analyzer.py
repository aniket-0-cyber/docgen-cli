from pathlib import Path
from typing import Dict, Any
from .base_analyzer import BaseAnalyzer

class CodeAnalyzer(BaseAnalyzer):
    def analyze_file(self) -> Dict[str, Any]:
        """
        Analyzes any source code file for AI documentation generation.
        Returns basic file information and content.
        """
        with open(self.path) as f:
            self.source = f.read()
        
        return {
            "file_path": str(self.path),
            "file_name": self.path.name,
            "extension": self.path.suffix,
            "source_code": self.source,
            "size": len(self.source)
        }

    def get_language_extensions(self) -> list[str]:
        """Return list of common programming file extensions."""
        return [
            '.py', '.js', '.ts', '.java', '.cpp', '.c',
            '.go', '.rs', '.php', '.rb', '.swift',
            '.kt', '.cs', '.scala', '.r', '.m'
        ]
