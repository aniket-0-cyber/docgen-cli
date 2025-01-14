# docgen/cli.py
import warnings
warnings.filterwarnings('ignore', category=Warning)

import typer
from rich.console import Console
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import glob
from docgen.config.config_handler import ConfigHandler
from docgen.analyzers.code_analyzer import CodeAnalyzer
from docgen.generators.ai_doc_generator import AIDocGenerator
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import time
import asyncio
from docgen.utils.git_utils import GitAnalyzer
from docgen.utils.extension import SUPPORTED_EXTENSIONS
from docgen.auth.api_key_manager import APIKeyManager
from docgen.auth.usage_tracker import UsageTracker
from docgen.utils.ai_client import AIClient

app = typer.Typer(
    help="""
────────────────────────── DocGen CLI v0.1.0 ──────────────────────────

Professional Documentation Generator\n
Generate comprehensive documentation for your codebase using AI-powered analysis.\n\n

Commands:\n
  • generate (g)   Generate documentation for files or directories\n
  • analyze        Analyze code structure and complexity\n
  • config         Configure DocGen settings and preferences\n
  • update (u)     Update docs for changed files (Git-aware)\n
  • clean (c)      Remove generated documentation files\n
  • version        Display DocGen version information\n
  • clear-cache    Clear the documentation generation cache\n\n

Quick Start:\n
  $ docgen generate --current-dir\n
  $ docgen g -f src/main.py\n
  $ docgen update\n\n

Examples:\n
  # Generate docs for current directory\n
  $ docgen generate --current-dir\n
  
  # Generate docs for a specific file\n
  $ docgen g -f src/main.py\n
  
  # Update documentation for changed files\n
  $ docgen update\n

  # Configure output format\n
  $ docgen config output_format html\n\n

Documentation: https://github.com/yourusername/docgen-cli#readme
""",
    short_help="Professional AI-powered documentation generator",
    no_args_is_help=True,
    add_completion=False,
)

console = Console()

class APIKeyRequired(Exception):
    """Raised when API key is missing or invalid."""
    pass

def _show_api_key_instructions():
    """Helper function to show API key instructions."""
    console.print("\nTo increase your limit, please:")
    console.print("1. Get an API key at: https://your-website.com/get-api-key")
    console.print("2. Run: docgen auth login --key YOUR_API_KEY")

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
    """Generate documentation for a file or directory."""
    try:
        # Check usage limits before processing
        usage_tracker = UsageTracker()
        can_request, _ = usage_tracker.can_make_request()
        
        if not can_request:
            console.print("[red]Monthly usage limit exceeded![/red]")
            console.print("To continue using DocGen, please:")
            console.print("1. Get an API key at: https://your-website.com/get-api-key")
            console.print("2. Run: docgen auth login --key YOUR_API_KEY")
            return

        # Validate path exists before proceeding
        if path and not path.exists():
            console.print(f"[red]Error: File not found: {path}[/red]")
            return
            
        asyncio.run(_generate_async(path, current_dir, output_dir, output_format))
        
        # Only track the request if we successfully generate documentation
        usage_tracker.track_request()
        console.print("[green]Documentation generated successfully![/green]")

        _, message = usage_tracker.can_make_request()
        console.print(f"[blue]{message}[/blue]")
        _show_api_key_instructions()

    except Exception as e:
        console.print(f"[red]Error generating documentation: {str(e)}[/red]")

async def _generate_async(
    path: Optional[Path],
    current_dir: bool,
    output_dir: Optional[Path],
    output_format: str,
):
    """Update documentation based on Git changes."""
    try:
        # Check usage limits before processing
        usage_tracker = UsageTracker()
        can_request, message = usage_tracker.can_make_request()
        
        if not can_request:
            console.print("[red]Monthly usage limit exceeded![/red]")
            console.print("To continue using DocGen, please:")
            console.print("1. Get an API key at: https://your-website.com/get-api-key")
            console.print("2. Run: docgen auth login --key YOUR_API_KEY")
            return
        
        
        start_time = time.time()
        base_path = Path.cwd()

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
            for ext in SUPPORTED_EXTENSIONS:
                files.extend(list(base_path.glob(f"*{ext}")))
        else:
            files = []
            for ext in SUPPORTED_EXTENSIONS:
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
                    if file_size > 2_000_000:  # Skip files larger than 2MB
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

        # Track the command after successful execution
        console.print("[green]Documentation update completed successfully![/green]")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

# Add command alias for shorter version
app.command(name="g", help="Alias for generate command")(generate)

@app.command(name="config", help="Configure DocGen settings and preferences")
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

@app.command(name="version", help="Display DocGen version information")
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

@app.command(name="update", help="Update documentation for changed files")
def update_docs(
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Output directory for documentation"),
    output_format: str = typer.Option("markdown", help="Output format (markdown/html)"),
    full_update: bool = typer.Option(False, "--full", "-f", help="Update entire documentation for changed files"),
    updates_file: Optional[str] = typer.Option(None, "--updates-file", "-u", 
        help="Store updates in a separate file (e.g., 'updates.md')")
):
    """Update documentation for changed files since last documentation generation."""
    try:
        # Check usage limits before processing
        usage_tracker = UsageTracker()
        can_request, message = usage_tracker.can_make_request()
        
        if not can_request:
            console.print("[red]Monthly usage limit exceeded![/red]")
            console.print("To continue using DocGen, please:")
            console.print("1. Get an API key at: https://your-website.com/get-api-key")
            console.print("2. Run: docgen auth login --key YOUR_API_KEY")
            raise typer.Exit(1)
        
        asyncio.run(_update_docs_async(output_dir, output_format, full_update, updates_file))
        
        # Only track the request if we successfully update documentation
        usage_tracker.track_request()
        console.print("[green]Documentation updated successfully![/green]")

        _, message = usage_tracker.can_make_request()
        console.print(f"[blue]{message}[/blue]")
        _show_api_key_instructions()

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error updating documentation: {str(e)}[/red]")
        raise typer.Exit(1)
    

async def _update_docs_async(
    output_dir: Optional[Path],
    output_format: str,
    full_update: bool,
    updates_file: Optional[str]
):
    try:
        # Check usage limits before processing
        usage_tracker = UsageTracker()
        can_request, message = usage_tracker.can_make_request()
        
        if not can_request:
            console.print("[red]Monthly usage limit exceeded![/red]")
            console.print("To continue using DocGen, please:")
            console.print("1. Get an API key at: https://your-website.com/get-api-key")
            console.print("2. Run: docgen auth login --key YOUR_API_KEY")
            raise typer.Exit(1)
        
        # Get changed files
        git_analyzer = GitAnalyzer()
        changed_files = git_analyzer.get_changed_files()
        
        if not changed_files:
            console.print("[yellow]No changes detected[/yellow]")
            return

        # Rest of the existing update code...
        base_path = Path.cwd().resolve()
        output_dir = output_dir.resolve() if output_dir else base_path
        
        updates_path = None
        if updates_file:
            updates_path = (output_dir / updates_file).resolve()
            if not updates_path.suffix:
                updates_path = updates_path.with_suffix('.md')
        
        # Process changed files
        files_data = []
        docs_results = {}
        
        for file_path, change_info in changed_files.items():
            try:
                if file_path.exists():
                    abs_path = file_path.resolve()
                    analyzer = CodeAnalyzer(abs_path)
                    analysis_result = analyzer.analyze_file()
                    rel_path = abs_path.relative_to(base_path)
                    files_data.append((
                        rel_path,
                        analysis_result,
                        change_info['full_code'],
                        change_info['changes']
                    ))
            except Exception as e:
                console.print(f"[yellow]Warning: Could not analyze {file_path}: {str(e)}[/yellow]")
        
        # Generate documentation
        ai_generator = AIDocGenerator()
        for file_path, analysis, code, changes in files_data:
            try:
                doc = await ai_generator.generate_update_documentation(code, changes)
                docs_results[file_path] = doc
            except Exception as e:
                console.print(f"[yellow]Warning: Could not generate update for {file_path}: {str(e)}[/yellow]")
        
        # Handle documentation updates
        doc_file = (output_dir / "codebase_documentation.md").resolve()
        if full_update:
            if doc_file.exists():
                update_existing_documentation(doc_file, docs_results, files_data)
                console.print(f"[green]Updated full documentation for {len(files_data)} files[/green]")
        else:
            if updates_path:
                add_incremental_update(updates_path, docs_results, files_data, create_if_missing=True)
                console.print(f"[green]Added updates to {updates_path.name}[/green]")
            elif doc_file.exists():
                add_incremental_update(doc_file, docs_results, files_data)
                console.print(f"[green]Added updates to main documentation[/green]")
            else:
                console.print("[yellow]No existing documentation found, generating new...[/yellow]")
                await _generate_async(None, False, output_dir, output_format)
        
        # Update last documented state
        git_analyzer.update_last_documented_state()

    except Exception as e:
        console.print(f"[red]Error updating documentation: {str(e)}[/red]")
        raise typer.Exit(1)

def update_existing_documentation(doc_file: Path, docs_results: Dict[Path, str], changed_files: List[Path]):
    """Update existing documentation file with changes."""
    try:
        content = doc_file.read_text()
        lines = content.split('\n')
        
        # Add updates section at the top if it doesn't exist
        if not any(line.startswith('## Recent Updates') for line in lines[:10]):
            update_section = [
                "## Recent Updates",
                f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
                "### Changed Files",
            ]
            lines = update_section + lines
        
        # Update the changes section
        update_index = lines.index("## Recent Updates")
        date_line = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        changed_files_list = "\n".join(f"- {f.relative_to(Path.cwd())}" for f in changed_files)
        
        # Insert updates
        lines[update_index + 1] = date_line
        lines[update_index + 2] = "### Changed Files"
        lines.insert(update_index + 3, changed_files_list)
        
        # Update individual file sections
        for file_path, new_doc in docs_results.items():
            rel_path = file_path.as_posix()
            file_header = f"## {rel_path}"
            try:
                file_start = next(i for i, line in enumerate(lines) if line.strip() == file_header)
                file_end = next((i for i, line in enumerate(lines[file_start + 1:], file_start + 1) 
                                 if line.startswith('## ') or line.startswith('---')), len(lines))
                
                # Replace old documentation with new
                lines[file_start:file_end] = [file_header, new_doc]
            except StopIteration:
                # File doesn't exist in documentation yet, append it
                lines.extend(["\n", file_header, new_doc, "---"])
        
        # Write updated content
        doc_file.write_text('\n'.join(lines))
        
    except Exception as e:
        raise ValueError(f"Error updating documentation file: {str(e)}")

def add_incremental_update(
    doc_file: Path, 
    docs_results: Dict[Path, str], 
    changed_files: List[tuple],
    create_if_missing: bool = False
):
    """Add an incremental update section at the top of the documentation."""
    try:
        # Create new update section
        timestamp = datetime.now()
        update_section = [
            f"## Documentation Update ({timestamp.strftime('%Y-%m-%d %H:%M:%S')})",
            "\n### Changed Files:",
            "\n".join(f"- {f[0]}" for f in changed_files),
            "\n### Updates:",
        ]
        
        # Add documentation updates for each changed file
        for file_path, new_doc in docs_results.items():
            update_section.extend([
                f"\n#### {file_path}",
                new_doc,
                "---"
            ])
        
        # Handle existing or new file
        if doc_file.exists():
            lines = doc_file.read_text().split('\n')
            
            # Find where to insert the update section
            if "# Recent Updates" in lines:
                insert_index = lines.index("# Recent Updates") + 1
            else:
                # Add Recent Updates header if it doesn't exist
                lines.insert(0, "\n# Recent Updates\n")
                insert_index = 1
            
            # Insert the new update section
            lines[insert_index:insert_index] = [""] + update_section + [""]
            content = '\n'.join(lines)
            
        elif create_if_missing:
            # Create new file with header and update
            content = "\n".join([
                "# Documentation Updates\n",
                f"Generated for: {Path.cwd().name}",
                f"First update: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n",
                "# Recent Updates\n"
            ] + update_section)
        else:
            raise FileNotFoundError(f"Documentation file not found: {doc_file}")
        
        # Ensure parent directory exists
        doc_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write updated content
        doc_file.write_text(content)
        
    except Exception as e:
        raise ValueError(f"Error adding incremental update: {str(e)}")

# Add command alias for shorter version
app.command(name="u", help="Alias for update command")(update_docs)

@app.command(name="auth")
def auth(
    command: str = typer.Argument(..., help="Login or logout"),
    api_key: Optional[str] = typer.Option(None, "--key", "-k", help="API key for login")
):
    """Manage authentication."""
    api_key_manager = APIKeyManager()
    
    if command.lower() == "login":
        if not api_key:
            console.print("[yellow]Please provide an API key using --key option[/yellow]")
            console.print("Get your API key at: https://your-website.com/get-api-key")
            raise typer.Exit(1)
            
        success, plan = api_key_manager.validate_api_key(api_key)
        if success:
            console.print(f"[green]Successfully logged in! Plan: {plan.title()}[/green]")
        else:
            console.print("[red]Invalid API key[/red]")
            raise typer.Exit(1)
            
    elif command.lower() == "logout":
        api_key_manager.set_api_key(None, None)  # Clear both key and plan
        console.print("[green]Successfully logged out[/green]")
        
    else:
        console.print("[red]Invalid command. Use 'login' or 'logout'[/red]")
        raise typer.Exit(1)

@app.command(name="usage")
def usage():
    """Show current usage statistics."""
    tracker = UsageTracker()
    usage_data = tracker._load_usage()  # Force reload to get current plan
    can_request, message = tracker.can_make_request()
    
    console.print("\n[bold]Current Usage Statistics[/bold]")
    
    if usage_data.get('api_key'):
        console.print(f"Plan: [green]{usage_data['plan'].title()}[/green] (API Key: {usage_data['api_key'][:8]}...)")
    else:
        console.print("Plan: [yellow]Anonymous[/yellow] (No API Key)")
    
    console.print(message)
    
    if not can_request:
        console.print("[red]You have reached your usage limit![/red]")
        _show_api_key_instructions()

def main():
    app()

if __name__ == "__main__":
    app()