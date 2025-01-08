# docgen/utils/git_utils.py
from git import Repo
from pathlib import Path
from typing import Dict, Optional
import re

class GitAnalyzer:
    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize GitAnalyzer with repository path.
        If no path is provided, assumes current directory.
        """
        self.repo_path = repo_path or Path.cwd()
        self.repo = Repo(self.repo_path)

    def get_pr_changes(self, pr_number: int) -> Dict:
        """
        Get changes introduced in a specific PR.
        """
        try:
            pr_branch = f"pull/{pr_number}/head"
            base_branch = self.repo.active_branch.name
            diff_index = self.repo.index.diff(pr_branch)
            return self._analyze_diff(diff_index)
        except Exception as e:
            raise ValueError(f"Error analyzing PR #{pr_number}: {str(e)}")

    def _analyze_diff(self, diff_index) -> Dict:
        """
        Analyze git diff and categorize changes.
        """
        changes = {
            "added_files": [],
            "modified_files": [],
            "deleted_files": [],
            "changes_by_type": {},
            "stats": {
                "total_additions": 0,
                "total_deletions": 0,
                "files_changed": 0
            }
        }

        for diff in diff_index:
            file_path = diff.a_path or diff.b_path
            file_type = Path(file_path).suffix

            if diff.new_file:
                changes["added_files"].append(file_path)
            elif diff.deleted_file:
                changes["deleted_files"].append(file_path)
            else:
                changes["modified_files"].append(file_path)

            if file_type not in changes["changes_by_type"]:
                changes["changes_by_type"][file_type] = {
                    "files": [],
                    "additions": 0,
                    "deletions": 0
                }
            
            changes["changes_by_type"][file_type]["files"].append(file_path)
            patch_stats = self._analyze_patch(diff.diff.decode('utf-8'))
            changes["stats"]["total_additions"] += patch_stats["additions"]
            changes["stats"]["total_deletions"] += patch_stats["deletions"]
            changes["changes_by_type"][file_type]["additions"] += patch_stats["additions"]
            changes["changes_by_type"][file_type]["deletions"] += patch_stats["deletions"]

        changes["stats"]["files_changed"] = (
            len(changes["modified_files"]) +
            len(changes["added_files"]) +
            len(changes["deleted_files"])
        )

        return changes

    def _analyze_patch(self, patch: str) -> Dict:
        """
        Analyze a git patch to count additions and deletions.
        """
        additions = len(re.findall(r'^\+[^+]', patch, re.MULTILINE))
        deletions = len(re.findall(r'^-[^-]', patch, re.MULTILINE))
        return {"additions": additions, "deletions": deletions}

    def generate_pr_summary(self, pr_number: int) -> str:
        """
        Generate a human-readable summary of PR changes.
        """
        changes = self.get_pr_changes(pr_number)
        
        summary_parts = [
            f"# Pull Request #{pr_number} Summary\n",
            "## Overview\n",
            f"- Files changed: {changes['stats']['files_changed']}",
            f"- Additions: {changes['stats']['total_additions']}",
            f"- Deletions: {changes['stats']['total_deletions']}\n",
        ]

        if changes["added_files"]:
            summary_parts.extend([
                "## Added Files",
                *[f"- {file}" for file in sorted(changes["added_files"])],
                ""
            ])

        if changes["modified_files"]:
            summary_parts.extend([
                "## Modified Files",
                *[f"- {file}" for file in sorted(changes["modified_files"])],
                ""
            ])

        if changes["deleted_files"]:
            summary_parts.extend([
                "## Deleted Files",
                *[f"- {file}" for file in sorted(changes["deleted_files"])],
                ""
            ])

        return "\n".join(summary_parts)