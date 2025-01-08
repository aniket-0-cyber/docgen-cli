import pytest
from unittest.mock import Mock, patch
from docgen.utils.git_utils import GitAnalyzer
from pathlib import Path

@pytest.fixture
def mock_repo():
    with patch('git.Repo') as mock:
        yield mock

def test_git_analyzer_init(mock_repo):
    analyzer = GitAnalyzer()
    assert analyzer.repo is not None
    mock_repo.assert_called_once()

def test_get_pr_changes(mock_repo):
    mock_diff = Mock()
    mock_diff.a_path = "test.py"
    mock_diff.b_path = "test.py"
    mock_diff.new_file = False
    mock_diff.deleted_file = False
    mock_diff.diff = b"+new\n-old"
    
    mock_repo.return_value.index.diff.return_value = [mock_diff]
    mock_repo.return_value.active_branch.name = "main"
    
    analyzer = GitAnalyzer()
    changes = analyzer.get_pr_changes(123)
    
    assert "modified_files" in changes
    assert "test.py" in changes["modified_files"]
    assert changes["stats"]["total_additions"] == 1
    assert changes["stats"]["total_deletions"] == 1

def test_pr_summary_generation(mock_repo):
    mock_diff = Mock()
    mock_diff.a_path = "test.py"
    mock_diff.b_path = "test.py"
    mock_diff.new_file = False
    mock_diff.deleted_file = False
    mock_diff.diff = b"+new\n-old"
    
    mock_repo.return_value.index.diff.return_value = [mock_diff]
    mock_repo.return_value.active_branch.name = "main"
    
    analyzer = GitAnalyzer()
    summary = analyzer.generate_pr_summary(123)
    
    assert "Pull Request #123 Summary" in summary
    assert "Files changed: 1" in summary
    assert "Modified Files" in summary
    assert "test.py" in summary

def test_analyze_patch():
    analyzer = GitAnalyzer()
    patch = "+new line\n-old line\n unchanged line"
    result = analyzer._analyze_patch(patch)
    
    assert result["additions"] == 1
    assert result["deletions"] == 1

def test_error_handling(mock_repo):
    mock_repo.return_value.index.diff.side_effect = Exception("Test error")
    
    analyzer = GitAnalyzer()
    with pytest.raises(ValueError) as exc_info:
        analyzer.get_pr_changes(123)
    
    assert "Error analyzing PR #123" in str(exc_info.value)