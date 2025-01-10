# docgen/analyzers/base_analyzer.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

class BaseAnalyzer(ABC):
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
        self.tree = None

    @abstractmethod
    def analyze_file(self) -> Dict[str, Any]:
        """
        Analyze a source code file and extract its structure.
        Must be implemented by language-specific analyzers.
        """
        pass