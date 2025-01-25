# docgen/generators/markdown_generator.py
from typing import Dict, Optional
from pathlib import Path

class MarkdownGenerator:
    def generate_file_documentation(self, analysis_result: Dict, output_path: Optional[Path] = None) -> str:
        """Generates comprehensive documentation for a file."""
        doc_parts = []
        
        # Module documentation
        if analysis_result.get("file_docstring"):
            doc_parts.append(analysis_result["file_docstring"])
        
        # Dependencies section
        if analysis_result.get("imports"):
            doc_parts.append("\n## Dependencies\n")
            for imp in analysis_result["imports"]:
                if imp["type"] == "import":
                    names = [n["name"] + (f" as {n['asname']}" if n["asname"] else "") 
                            for n in imp["names"]]
                    doc_parts.append(f"- `import {', '.join(names)}`")
                else:
                    names = [n["name"] + (f" as {n['asname']}" if n["asname"] else "") 
                            for n in imp["names"]]
                    doc_parts.append(f"- `from {imp['module']} import {', '.join(names)}`")
        
        # Class documentation
        if analysis_result.get("classes"):
            doc_parts.append("\n## Classes\n")
            for class_info in analysis_result["classes"]:
                doc_parts.append(self._generate_class_markdown(class_info))
                
                # Add inheritance information
                inheritance = [rel for rel in analysis_result["relationships"]["inheritance"] 
                             if rel["class"] == class_info["name"]]
                if inheritance:
                    doc_parts.append("\n### Inheritance\n")
                    for inh in inheritance:
                        doc_parts.append(f"- Inherits from: `{inh['inherits_from']}`")
        
        # Function documentation
        if analysis_result.get("functions"):
            doc_parts.append("\n## Functions\n")
            for function_info in analysis_result["functions"]:
                doc_parts.append(self._generate_function_markdown(function_info))
                
                # Add function relationships
                calls = [rel for rel in analysis_result["relationships"]["function_calls"] 
                        if rel["caller"] == function_info["name"]]
                if calls:
                    doc_parts.append("\n### Function Calls\n")
                    for call in calls:
                        doc_parts.append(f"- Calls: `{call['called']}`")
        
        markdown_content = "\n".join(doc_parts)
        
        if output_path:
            output_path.write_text(markdown_content)
            
        return markdown_content

    def _generate_class_markdown(self, class_info: Dict) -> str:
        parts = [
            f"### {class_info['name']}\n",
            f"```class {class_info['name']}({', '.join(class_info['bases'])})\n```\n"
        ]
        
        if class_info.get("docstring"):
            parts.append(f"{class_info['docstring']}\n")
            
        if class_info.get("methods"):
            parts.append("#### Methods\n")
            for method in class_info["methods"]:
                parts.append(self._generate_function_markdown(method, is_method=True))
                
        return "\n".join(parts)

    def _generate_function_markdown(self, function_info: Dict, is_method: bool = False) -> str:
        """Generate markdown documentation for a function or method."""
        parts = []
        prefix = "#### " if is_method else "### "
        
        # Function signature
        signature = f"{function_info['name']}({', '.join(function_info['args'])})"
        if function_info.get('returns'):
            signature += f" -> {function_info['returns']}"
        
        parts.extend([
            f"{prefix}{function_info['name']}\n",
            f"```{signature}\n```\n"
        ])
        
        # Docstring
        if function_info.get('docstring'):
            parts.append(f"{function_info['docstring']}\n")
        
        # Source code (optional)
        if function_info.get('source'):
            parts.extend([
                "**Source:**\n",
                f"```{function_info['source']}\n```\n"
            ])
        
        return "\n".join(parts)
