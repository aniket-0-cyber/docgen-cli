# docgen/utils/git_utils.py
from docgen.utils.extension import SUPPORTED_EXTENSIONS
from rich.console import Console
from git import Repo
from pathlib import Path
from typing import Dict
import json
from datetime import datetime

console = Console()

class GitAnalyzer:
    def __init__(self):
        try:
            self.repo = Repo(".")
        except Exception:
            raise ValueError("Not a git repository")
        
        # Create .docgen directory if it doesn't exist
        self.docgen_dir = Path(".docgen")
        self.docgen_dir.mkdir(exist_ok=True)
        self.last_doc_state_file = self.docgen_dir / "last_state.json"

    def get_changed_files(self) -> Dict[Path, Dict]:
        """Get files changed since last documentation update with their changes."""
        try:
            console.print("[blue]Checking for changed files...[/blue]")
            changed = {}
            
            # Get all changes at once using git diff-index
            diff_index = self.repo.head.commit.diff(None, create_patch=True)
            
            # Process all changes in a single pass
            for diff in diff_index:
                if not diff.a_path:
                    continue
                    
                path = Path(diff.a_path)
                
                # Skip non-supported files
                if path.suffix not in SUPPORTED_EXTENSIONS:
                    continue
                
                try:
                    # Get patch directly from diff object
                    patch = ''
                    if hasattr(diff, 'diff'):
                        try:
                            patch = diff.diff.decode('utf-8')
                        except (AttributeError, UnicodeDecodeError):
                            pass
                    
                    # Only read the file if it exists
                    if path.exists():
                        try:
                            with open(path, 'r', encoding='utf-8') as f:
                                new_content = f.read()
                        except UnicodeDecodeError:
                            continue
                    else:
                        new_content = ''
                    
                    # Only add files that have actual changes or content
                    if patch or new_content:
                        changed[path] = {
                            'type': 'modified',
                            'changes': patch,
                            'full_code': new_content
                        }
                except Exception as e:
                    console.print(f"[yellow]Warning: Skipping {path} due to error: {str(e)}[/yellow]")
                    continue
            
            # Handle untracked files
            for untracked_file in self.repo.untracked_files:
                path = Path(untracked_file)
                
                # Skip non-supported and hidden files
                if (path.suffix not in SUPPORTED_EXTENSIONS or
                    any(p in str(path) for p in ['.docgen', '__pycache__', '.git'])):
                    continue
                
                if path.exists():
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        changed[path] = {
                            'type': 'new',
                            'changes': f"+++ {path}\n{content}",
                            'full_code': content
                        }
                    except UnicodeDecodeError:
                        continue
            
            # Output results
            if changed:
                console.print(f"\n[blue]Found {len(changed)} changed files:[/blue]")
                for file, info in changed.items():
                    console.print(f"- {file} ({info['type']})")
                    if info['changes']:
                        console.print("  [green]Changes detected[/green]")
            else:
                console.print("[yellow]No changes detected[/yellow]")
            
            return changed
            
        except Exception as e:
            console.print(f"[red]Error getting changed files: {str(e)}[/red]")
            console.print(f"[red]Exception type: {type(e).__name__}[/red]")
            return {}

    def update_last_documented_state(self):
        """Update the last documented state."""
        try:
            current_state = {
                'last_commit': self.repo.head.commit.hexsha,
                'timestamp': datetime.now().isoformat(),
                'branch': self.repo.active_branch.name
            }
            
            self.last_doc_state_file.write_text(json.dumps(current_state, indent=2))
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not update documentation state: {str(e)}[/yellow]")