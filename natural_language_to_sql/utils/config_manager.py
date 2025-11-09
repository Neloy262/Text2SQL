"""
Configuration management for the Natural Language to SQL application.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages configuration for the NSQL application."""
    
    def __init__(self):
        # Use user's home directory for config
        self.config_dir = Path.home() / ".nsql"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize with default values
        self.default_config = {
            "db_url": "",
            "table_descriptions_file": "",
            "gemini_model": "gemini-1.5-pro-latest"
        }
        
        # Load existing config or create new one
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    config = self.default_config.copy()
                    config.update(loaded_config)
                    return config
            except Exception:
                # If there's an error loading the config, return defaults
                return self.default_config.copy()
        else:
            return self.default_config.copy()
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def set_db_url(self, db_url: str):
        """Set the database URL in the configuration."""
        self.config['db_url'] = db_url
    
    def set_table_descriptions_file(self, file_path: str):
        """Set the table descriptions file path in the configuration."""
        self.config['table_descriptions_file'] = file_path
    
    def set_gemini_model(self, model: str):
        """Set the Gemini model in the configuration."""
        self.config['gemini_model'] = model
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration."""
        return self.config.copy()
    
    def get_db_url(self) -> Optional[str]:
        """Get the configured database URL."""
        return self.config.get('db_url', '')
    
    def get_table_descriptions_file(self) -> Optional[str]:
        """Get the configured table descriptions file."""
        return self.config.get('table_descriptions_file', '')
    
    def get_gemini_model(self) -> str:
        """Get the configured Gemini model."""
        return self.config.get('gemini_model', 'gemini-1.5-pro-latest')
    
    def reset_config(self):
        """Reset configuration to defaults."""
        self.config = self.default_config.copy()
        self.save_config()


# Global configuration manager instance
config_manager = ConfigManager()