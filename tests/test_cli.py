# tests/test_cli.py
from typer.testing import CliRunner
from docgen.cli import app
import pytest

runner = CliRunner()

def test_cli_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "DocGen" in result.stdout

def test_cli_analyze_nonexistent():
    result = runner.invoke(app, ["analyze", "nonexistent/path"])
    assert result.exit_code == 1
    assert "Error" in result.stdout

def test_cli_analyze_valid(tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass")
    
    result = runner.invoke(app, ["analyze", str(test_file)])
    assert result.exit_code == 0
    assert "Analysis complete" in result.stdout
