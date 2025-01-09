# docgen/utils/git_utils.py
from rich.console import Console
from git import Repo
from pathlib import Path
from typing import Dict, List, Optional
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
            
            # Get unstaged changes
            for diff in self.repo.head.commit.diff(None):
                if diff.a_path:
                    path = Path(diff.a_path)
                    # Get both old and new versions of the file
                    old_content = diff.a_blob.data_stream.read().decode('utf-8') if diff.a_blob else ''
                    new_content = path.read_text() if path.exists() else ''
                    
                    # Create a unified diff
                    changes = f"--- {diff.a_path}\n+++ {diff.b_path}\n"
                    changes += ''.join(
                        f"{line}\n" for line in new_content.split('\n')
                        if line.strip()
                    )
                    
                    changed[path] = {
                        'type': 'modified',
                        'changes': changes,
                        'full_code': new_content
                    }
            
            # Get staged changes
            for diff in self.repo.index.diff('HEAD'):
                if diff.a_path:
                    path = Path(diff.a_path)
                    if path not in changed:  # Don't override unstaged changes
                        # Get both versions
                        old_content = diff.a_blob.data_stream.read().decode('utf-8') if diff.a_blob else ''
                        new_content = self.repo.index.blob(diff.b_path).data_stream.read().decode('utf-8') if diff.b_path else ''
                        
                        # Create a unified diff
                        changes = f"--- {diff.a_path}\n+++ {diff.b_path}\n"
                        changes += ''.join(
                            f"{line}\n" for line in new_content.split('\n')
                            if line.strip()
                        )
                        
                        changed[path] = {
                            'type': 'modified',
                            'changes': changes,
                            'full_code': new_content
                        }
            
            # Get untracked files
            untracked = [
                Path(f) for f in self.repo.untracked_files
                if not any(p in str(f) for p in ['.docgen', '__pycache__', '.git'])
            ]
            
            # Add untracked files
            for path in untracked:
                if path.exists():
                    content = path.read_text()
                    changed[path] = {
                        'type': 'new',
                        'changes': f"--- /dev/null\n+++ {path}\n{content}",
                        'full_code': content
                    }
            
            # Debug output
            if changed:
                console.print("\n[blue]Changed files:[/blue]")
                for file, info in changed.items():
                    console.print(f"- {file} ({info['type']})")
            else:
                console.print("[yellow]No changes detected[/yellow]")
            
            return changed
            
        except Exception as e:
            console.print(f"[red]Error getting changed files: {str(e)}[/red]")
            console.print(f"[red]Exception details: {type(e).__name__}[/red]")
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