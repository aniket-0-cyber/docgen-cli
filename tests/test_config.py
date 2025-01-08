from docgen.config.config_handler import ConfigHandler
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        config = ConfigHandler()
        config.app_dir = Path(tmpdir)
        config.config_path = Path(tmpdir) / "config.json"
        yield config
        # Cleanup happens automatically when the context manager exits

def test_config_defaults(temp_config):
    assert temp_config.get("template_style") == "google"
    assert temp_config.get("output_format") == "markdown"
    assert not temp_config.get("recursive")

def test_config_set_get(temp_config):
    temp_config.set("template_style", "numpy")
    assert temp_config.get("template_style") == "numpy"

def test_config_save_load(temp_config):
    temp_config.set("template_style", "numpy")
    temp_config.save()
    
    new_config = ConfigHandler()
    new_config.app_dir = temp_config.app_dir
    new_config.config_path = temp_config.config_path
    new_config.load()
    
    assert new_config.get("template_style") == "numpy"

def test_config_invalid_json(temp_config):
    temp_config.config_path.write_text("{invalid json")
    new_config = ConfigHandler()
    new_config.app_dir = temp_config.app_dir
    new_config.config_path = temp_config.config_path
    new_config.load()
    assert new_config.get("template_style") == "google"  # Should fall back to defaults

def test_config_missing_file(temp_config):
    temp_config.config_path.unlink(missing_ok=True)
    new_config = ConfigHandler()
    new_config.app_dir = temp_config.app_dir
    new_config.config_path = temp_config.config_path
    assert new_config.get("template_style") == "google"

# def test_config_invalid_values(temp_config):
#     with pytest.raises(ValueError):
#         temp_config.set("template_style", "invalid_style")
#     with pytest.raises(ValueError):
#         temp_config.set("output_format", "invalid_format")