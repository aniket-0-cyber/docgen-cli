from docgen.generators.docstring_generator import DocstringGenerator
from docgen.generators.markdown_generator import MarkdownGenerator

def test_docstring_generation():
    generator = DocstringGenerator()
    
    function_info = {
        "name": "calculate_average",
        "args": ["numbers", "weights"],
        "returns": "float",
        "docstring": None
    }
    
    docstring = generator.generate_function_docstring(function_info)
    
    assert "calculate average" in docstring.lower()
    assert "Args:" in docstring
    assert "Returns:" in docstring
    assert "numbers" in docstring
    assert "weights" in docstring

def test_markdown_generation():
    generator = MarkdownGenerator()
    
    analysis_result = {
        "file_docstring": "Test module",
        "classes": [{
            "name": "TestClass",
            "bases": ["object"],
            "methods": [{
                "name": "test_method",
                "args": ["self", "param1"],
                "returns": "str",
                "docstring": "Test method docstring"
            }],
            "docstring": "Test class docstring"
        }],
        "functions": [{
            "name": "test_function",
            "args": ["arg1", "arg2"],
            "returns": "bool",
            "docstring": "Test function docstring"
        }]
    }
    
    markdown = generator.generate_file_documentation(analysis_result)
    assert "# Module Documentation" in markdown
    assert "## Classes" in markdown
    assert "### TestClass" in markdown
    assert "## Functions" in markdown
    assert "### test_function" in markdown