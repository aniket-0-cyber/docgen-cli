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

    def get_changed_files(self) -> List[Path]:
        """Get files changed since last documentation update."""
        try:
            console.print("[blue]Checking for changed files...[/blue]")
            
            changed = []
            
            # Get unstaged changes
            for item in self.repo.index.diff(None):
                if item.a_path:
                    changed.append(Path(item.a_path))
                if item.b_path and item.b_path != item.a_path:
                    changed.append(Path(item.b_path))
            
            # Get staged changes
            for item in self.repo.index.diff('HEAD'):
                if item.a_path:
                    changed.append(Path(item.a_path))
                if item.b_path and item.b_path != item.a_path:
                    changed.append(Path(item.b_path))
            
            # Get untracked files that are not ignored
            untracked = [
                Path(f) for f in self.repo.untracked_files
                if not any(p in str(f) for p in ['.docgen', '__pycache__', '.git'])
            ]
            changed.extend(untracked)
            
            # Remove duplicates and sort
            changed = sorted(set(changed))
            
            console.print(f"[blue]Found changes:[/blue]")
            console.print(f"- Unstaged/staged changes: {len(changed) - len(untracked)}")
            console.print(f"- New untracked files: {len(untracked)}")
            
            if changed:
                console.print("\n[blue]Changed files:[/blue]")
                for file in changed:
                    console.print(f"- {file}")
            
            return changed
            
        except Exception as e:
            console.print(f"[red]Error getting changed files: {str(e)}[/red]")
            return []

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