# docgen/cli.py
import warnings
warnings.filterwarnings('ignore', category=Warning)

import typer
from rich.console import Console
from pathlib import Path
from typing import Optional
import glob
from docgen.config.config_handler import ConfigHandler
from docgen.analyzers.code_analyzer import CodeAnalyzer
from docgen.generators.ai_doc_generator import AIDocGenerator
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import time
import asyncio

app = typer.Typer(help="DocGen CLI - Automated Documentation Generator")
console = Console()

async def process_file(path: Path, output_format: str, output_dir: Optional[Path] = None) -> None:
    """Process any source code file and generate documentation."""
    try:
        analyzer = CodeAnalyzer(path)
        analysis_result = analyzer.analyze_file()
        source_code = path.read_text()
        
        # Generate AI documentation
        ai_generator = AIDocGenerator()
        documentation = await ai_generator.generate_documentation_batch([
            (path, analysis_result, source_code)
        ])
        
        # Get the documentation for the single file
        doc_content = documentation.get(path, "Error: Documentation generation failed")
        
        # Save documentation
        if output_dir:
            output_path = output_dir / f"{path.stem}.md"
        else:
            output_path = path.with_suffix('.md')
            
        output_path.write_text(doc_content)
        console.print(f"[green]Generated AI documentation for {path} -> {output_path}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error processing {path}: {str(e)}[/red]")

def should_process_file(file_path: Path, base_path: Path) -> bool:
    """Check if the file should be processed."""
    exclude_patterns = {
        'venv', 'env', '.env',
        'site-packages', 
        '__pycache__',
        '.git',
        '.pytest_cache',
        'build', 'dist',
        '*.egg-info',
        'node_modules'
    }
    
    rel_path = str(file_path.relative_to(base_path))
    return not any(pattern in rel_path for pattern in exclude_patterns)

@app.command(name="generate", help="Generate documentation for code", short_help="Generate docs")
def generate(
    path: Optional[Path] = typer.Option(None, "--file", "-f", help="Path to specific file"),
    current_dir: bool = typer.Option(False, "--current-dir", "-cd", help="Generate docs for current directory"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Output directory for documentation"),
    output_format: str = typer.Option("markdown", help="Output format (markdown/html)"),
):
    """Generate documentation for your codebase."""
    asyncio.run(_generate_async(path, current_dir, output_dir, output_format))

async def _generate_async(
    path: Optional[Path],
    current_dir: bool,
    output_dir: Optional[Path],
    output_format: str,
):
    """Async function to generate documentation."""
    try:
        start_time = time.time()
        base_path = Path.cwd()
        
        # Get supported extensions first
        extensions = [
            '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c',
            '.go', '.rs', '.php', '.rb', '.swift',
            '.kt', '.cs', '.scala', '.r', '.m'
        ]

        if path:  # Single file mode
            if not path.exists():
                console.print(f"[red]Error: File not found: {path}[/red]")
                raise typer.Exit(1)
            if not path.is_file():
                console.print(f"[red]Error: Path is not a file: {path}[/red]")
                raise typer.Exit(1)
            await process_file(path, output_format, output_dir)
            return

        # Directory mode (current dir or full codebase)
        if current_dir:
            files = []
            for ext in extensions:
                files.extend(list(base_path.glob(f"*{ext}")))
        else:
            files = []
            for ext in extensions:
                files.extend(list(base_path.rglob(f"*{ext}")))

        source_files = [f for f in files if should_process_file(f, base_path)]
        
        if not source_files:
            console.print("[yellow]No source code files found to process[/yellow]")
            raise typer.Exit(1)

        # Prepare batch processing data
        files_data = []
        total_size = 0
        with console.status("[bold green]Analyzing files...") as status:
            for file_path in source_files:
                try:
                    # Skip large files
                    file_size = file_path.stat().st_size
                    if file_size > 1_000_000:  # Skip files larger than 1MB
                        console.print(f"[yellow]Skipping large file: {file_path}[/yellow]")
                        continue
                    
                    total_size += file_size
                    source_code = file_path.read_text()
                    analyzer = CodeAnalyzer(file_path)
                    analysis_result = analyzer.analyze_file()
                    files_data.append((file_path, analysis_result, source_code))
                except Exception as e:
                    console.print(f"[yellow]Warning: Error analyzing {file_path}: {str(e)}[/yellow]")

        # Generate documentation asynchronously
        ai_generator = AIDocGenerator()
        with console.status("[bold green]Generating documentation...") as status:
            docs_results = await ai_generator.generate_documentation_batch(files_data)

        # Combine documentation
        output_filename = "codebase_documentation.md" if not current_dir else "directory_documentation.md"
        output_path = (output_dir or base_path) / output_filename

        combined_docs = []
        scope = "Codebase" if not current_dir else "Current Directory"
        combined_docs.extend([
            f"# {scope} Documentation\n",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n",
            "## Table of Contents\n"
        ])

        # Add table of contents
        for file_path in sorted(source_files):
            rel_path = file_path.relative_to(base_path)
            combined_docs.append(f"- [{rel_path}](#{rel_path.as_posix().replace('/', '-')})\n")

        # Add file documentation
        for file_path in sorted(source_files):
            rel_path = file_path.relative_to(base_path)
            anchor = rel_path.as_posix().replace('/', '-')
            combined_docs.extend([
                f"\n<a id='{anchor}'></a>\n",
                f"## {rel_path}\n",
                docs_results.get(file_path, "Error: Documentation generation failed"),
                "\n---\n"
            ])

        # Write combined documentation
        output_path.write_text("\n".join(combined_docs))
        
        elapsed_time = time.time() - start_time
        console.print(f"[green]Documentation generated: {output_path}[/green]")
        console.print(f"[blue]Time taken: {elapsed_time:.2f} seconds[/blue]")
        console.print(f"[blue]Processed {len(files_data)} source files ({total_size/1024:.1f} KB)[/blue]")

    except Exception as e:
        console.print(f"[red]Error generating documentation: {str(e)}[/red]")
        raise typer.Exit(1)

# Add command alias for shorter version
app.command(name="g", help="Alias for generate command")(generate)

@app.command()
def analyze(
    path: Path = typer.Argument(..., help="Path to the source code directory or file"),
    output_format: str = typer.Option("markdown", help="Output format (markdown/html)"),
    recursive: bool = typer.Option(False, help="Recursively process directories")
):
    """Analyze source code and generate documentation."""
    try:
        if not path.exists():
            console.print(f"[red]Error: Path does not exist: {path}[/red]")
            raise typer.Exit(1)
            
        console.print(f"Analyzing code at: {path}")
        
        config_handler = ConfigHandler()
        config_handler.set("output_format", output_format)
        config_handler.set("recursive", recursive)
        
        if path.is_file():
            process_file(path, output_format)
        else:
            analyzer = CodeAnalyzer(Path())  # Temporary instance to get extensions
            extensions = analyzer.get_language_extensions()
            pattern = f"**/*{{{','.join(extensions)}}}" if recursive else f"*{{{','.join(extensions)}}}"
            files = glob.glob(str(path / pattern), recursive=recursive)
            
            with console.status("[bold green]Processing files...") as status:
                for file_path in files:
                    process_file(Path(file_path), output_format)
                    
        console.print("[green]Documentation generation completed![/green]")

    except Exception as e:
        console.print(f"[red]Error analyzing code: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command()
def config(
    key: str = typer.Argument(..., help="Configuration key to get/set"),
    value: Optional[str] = typer.Option(None, help="Value to set (if not provided, shows current value)")
):
    """Manage DocGen configuration."""
    config_handler = ConfigHandler()
    if value is None:
        console.print(f"{key}: {config_handler.get(key)}")
    else:
        config_handler.set(key, value)
        config_handler.save()
        console.print(f"Updated {key} to: {value}")

@app.command()
def version():
    """Show the version of DocGen."""
    import pkg_resources
    version = pkg_resources.get_distribution("docgen-cli").version
    console.print(f"DocGen CLI version: {version}")

@app.command(name="clean", help="Clean up generated documentation files")
def clean(
    current_dir: bool = typer.Option(False, "--current-dir", "-cd", help="Clean only current directory")
):
    """Clean up all generated documentation files except README.md."""
    try:
        base_path = Path.cwd() if current_dir else Path.cwd().resolve()
        
        # Find all .md files
        pattern = "*.md"
        md_files = base_path.glob(pattern) if current_dir else base_path.rglob(pattern)
        
        deleted_count = 0
        for file_path in md_files:
            # Skip README.md and files in excluded directories
            if (file_path.name.lower() == "readme.md" or 
                not should_process_file(file_path, base_path)):
                continue
                
            try:
                file_path.unlink()
                deleted_count += 1
                console.print(f"[green]Deleted: {file_path}[/green]")
            except Exception as e:
                console.print(f"[yellow]Could not delete {file_path}: {e}[/yellow]")
        
        console.print(f"[bold green]Cleanup completed! Deleted {deleted_count} documentation files.[/bold green]")

    except Exception as e:
        console.print(f"[red]Error during cleanup: {str(e)}[/red]")
        raise typer.Exit(1)

# Add command alias for shorter version
app.command(name="c", help="Alias for clean command")(clean)

@app.command(name="clear-cache")
def clean_cache():
    """Clean the documentation cache."""
    try:
        cache_dir = Path.home() / '.docgen' / 'cache'
        if cache_dir.exists():
            # Remove all cache files
            for cache_file in cache_dir.glob('*.json'):
                cache_file.unlink()
            cache_dir.rmdir()
            console.print("[green]Cache cleaned successfully![/green]")
        else:
            console.print("[yellow]Cache directory doesn't exist.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error cleaning cache: {str(e)}[/red]")
        raise typer.Exit(1)

def main():
    app()

if __name__ == "__main__":
    app()