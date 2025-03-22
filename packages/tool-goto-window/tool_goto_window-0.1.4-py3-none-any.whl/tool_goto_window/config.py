import os
import toml
from pathlib import Path
from typing import Dict, Optional

DEFAULT_CONFIG = """# tool-goto-window configuration
# Format: 
# [shortcuts]
# shortcut_name = { browser = "chrome", url = "https://example.com" }

[shortcuts]
# Example shortcuts (uncomment and modify as needed):
# calendar = { browser = "chrome", url = "https://calendar.google.com" }
# mail = { browser = "chrome", url = "https://mail.google.com" }
# chat = { browser = "chrome", url = "https://chat.google.com" }
"""

def get_config_path() -> Path:
    """Get the path to the config file"""
    config_dir = os.path.expanduser("~/.config/tool-goto-window")
    return Path(config_dir) / "config.toml"

def load_config() -> Dict:
    """Load the configuration file"""
    config_path = get_config_path()
    if not config_path.exists():
        return {}
    
    return toml.load(config_path)

def init_config():
    """Initialize the config file with default values"""
    config_path = get_config_path()
    
    # Create directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Don't overwrite if exists
    if config_path.exists():
        print(f"Config already exists at {config_path}")
        return
    
    # Write default config
    config_path.write_text(DEFAULT_CONFIG)
    print(f"Created default config at {config_path}") 