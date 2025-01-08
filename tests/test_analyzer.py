# tests/test_analyzer.py
import pytest
from pathlib import Path
from docgen.analyzers.python_analyzer import PythonAnalyzer

def test_python_analyzer():
    test_content = '''
def example_function(a: int, b: str) -> bool:
    """
    This is a test function.
    """
    return True

class ExampleClass:
    """
    This is a test class.
    """
    def method1(self, x):
        return x
    '''
    
    tmp_file = Path("test_file.py")
    tmp_file.write_text(test_content)
    
    try:
        analyzer = PythonAnalyzer(tmp_file)
        result = analyzer.analyze_file()
        
        # Check function analysis
        assert len(result["functions"]) == 1
        assert result["functions"][0].name == "example_function"
        assert result["functions"][0].args == ["a", "b"]
        assert result["functions"][0].returns == "bool"
        assert result["functions"][0].docstring is not None
        
        # Check class analysis
        assert len(result["classes"]) == 1
        assert result["classes"][0].name == "ExampleClass"
        assert result["classes"][0].docstring is not None
        assert len(result["classes"][0].methods) == 1
        
    finally:
        tmp_file.unlink()