# docgen/analyzers/python_analyzer.py
import ast
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional, Any
from .base_analyzer import BaseAnalyzer

@dataclass
class FunctionInfo:
    name: str
    args: List[str]
    returns: Optional[str]
    docstring: Optional[str]
    source: str
    lineno: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ClassInfo:
    name: str
    methods: List[FunctionInfo]
    docstring: Optional[str]
    bases: List[str]
    source: str
    lineno: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "methods": [method.to_dict() for method in self.methods],
            "docstring": self.docstring,
            "bases": self.bases,
            "source": self.source,
            "lineno": self.lineno
        }

class NodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.parent = None
        self.parents = {}

    def visit(self, node):
        temp = self.parent
        self.parent = node
        self.parents[node] = temp
        super().generic_visit(node)
        self.parent = temp

class PythonAnalyzer(BaseAnalyzer):
    def analyze_file(self) -> Dict[str, Any]:
        """
        Analyzes a Python source file and extracts its structure, relationships, and documentation.
        
        This analyzer:
        1. Parses the Python file into an AST
        2. Tracks parent-child relationships between nodes
        3. Extracts classes, methods, functions, and their documentation
        4. Analyzes dependencies and code relationships
        
        Returns:
            Dict containing:
            - file_docstring: Module-level documentation
            - imports: List of module dependencies
            - classes: List of class definitions and their methods
            - functions: List of top-level functions
            - relationships: Code dependencies and relationships
        """
        with open(self.path) as f:
            self.source = f.read()
        
        tree = ast.parse(self.source)
        
        # Add parent references to nodes
        visitor = NodeVisitor()
        visitor.visit(tree)
        self.parents = visitor.parents
        
        # Analyze imports and dependencies
        imports = self._analyze_imports(tree)
        
        result = {
            "file_docstring": self._format_docstring(ast.get_docstring(tree)),
            "imports": imports,
            "classes": [],
            "functions": [],
            "relationships": self._analyze_relationships(tree)
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                result["classes"].append(self._analyze_class(node))
            elif isinstance(node, ast.FunctionDef):
                parent = self.parents.get(node)
                if isinstance(parent, ast.Module):
                    result["functions"].append(self._analyze_function(node))
        
        result["classes"] = [cls.to_dict() for cls in result["classes"]]
        result["functions"] = [func.to_dict() for func in result["functions"]]
        
        return result

    def _analyze_imports(self, tree: ast.AST) -> List[Dict[str, str]]:
        """Analyzes module imports and their usage."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_info = {
                    "type": "import" if isinstance(node, ast.Import) else "from",
                    "names": [],
                    "module": node.module if isinstance(node, ast.ImportFrom) else None,
                    "lineno": node.lineno
                }
                for name in node.names:
                    import_info["names"].append({
                        "name": name.name,
                        "asname": name.asname
                    })
                imports.append(import_info)
        return imports

    def _analyze_relationships(self, tree: ast.AST) -> Dict[str, List[str]]:
        """
        Analyzes code relationships including:
        - Class inheritance
        - Function calls
        - Method overrides
        - Variable dependencies
        """
        relationships = {
            "inheritance": [],
            "function_calls": [],
            "method_overrides": [],
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        relationships["inheritance"].append({
                            "class": node.name,
                            "inherits_from": base.id
                        })
            
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    relationships["function_calls"].append({
                        "caller": self._get_parent_function_name(node),
                        "called": node.func.id
                    })
        
        return relationships

    def _format_docstring(self, docstring: Optional[str]) -> str:
        """
        Formats docstring with improved readability and extracts:
        - Description
        - Parameters
        - Returns
        - Examples
        - Notes
        """
        if not docstring:
            return ""
            
        parts = []
        lines = docstring.split("\n")
        
        # Extract main description
        desc_lines = []
        for line in lines:
            if line.strip().lower().startswith(("args:", "returns:", "example:", "note:")):
                break
            desc_lines.append(line.strip())
        
        if desc_lines:
            parts.append("### Description\n" + "\n".join(desc_lines) + "\n")
        
        # Extract other sections
        current_section = None
        section_content = []
        
        for line in lines:
            line = line.strip()
            lower_line = line.lower()
            
            if lower_line.startswith(("args:", "returns:", "example:", "note:")):
                if current_section and section_content:
                    parts.append(f"### {current_section}\n" + "\n".join(section_content) + "\n")
                    section_content = []
                current_section = line.split(":")[0].strip()
            elif line and current_section:
                section_content.append(line)
                
        if current_section and section_content:
            parts.append(f"### {current_section}\n" + "\n".join(section_content) + "\n")
            
        return "\n".join(parts)

    def _get_parent_function_name(self, node: ast.AST) -> Optional[str]:
        """Gets the name of the function containing this node."""
        current = node
        while current:
            if isinstance(current, ast.FunctionDef):
                return current.name
            current = self.parents.get(current)
        return None

    def _analyze_function(self, node: ast.FunctionDef) -> FunctionInfo:
        """Analyze a function node and extract its information."""
        args = [arg.arg for arg in node.args.args]
        returns = None
        if node.returns:
            returns = ast.unparse(node.returns) if hasattr(ast, 'unparse') else self._get_node_source(node.returns)
        
        return FunctionInfo(
            name=node.name,
            args=args,
            returns=returns,
            docstring=ast.get_docstring(node),
            source=self._get_node_source(node),
            lineno=node.lineno
        )

    def _analyze_class(self, node: ast.ClassDef) -> ClassInfo:
        """Analyze a class node and extract its information."""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(self._analyze_function(item))
        
        bases = [ast.unparse(base) if hasattr(ast, 'unparse') else self._get_node_source(base) 
                for base in node.bases]
        
        return ClassInfo(
            name=node.name,
            methods=methods,
            docstring=ast.get_docstring(node),
            bases=bases,
            source=self._get_node_source(node),
            lineno=node.lineno
        )

    def _get_node_source(self, node: ast.AST) -> str:
        """Get the source code for an AST node."""
        if hasattr(ast, 'unparse'):  # Python 3.9+
            return ast.unparse(node)
        else:
            # Fallback for older Python versions
            lines = self.source.splitlines()
            return '\n'.join(lines[node.lineno-1:node.end_lineno])

    def get_language_extensions(self) -> list[str]:
        """Return list of file extensions supported by this analyzer."""
        return ['.py']
