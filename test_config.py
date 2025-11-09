#!/usr/bin/env python3
"""
Test script for the configuration functionality of the Natural Language to SQL application.
"""
import tempfile
import os
from natural_language_to_sql.utils.config_manager import config_manager


def test_config():
    """Test the configuration management functionality."""
    print("Testing Configuration Management...")
    
    # Reset config to start fresh
    config_manager.reset_config()
    print("1. Configuration reset to defaults")
    
    # Test setting database URL
    test_db_url = "sqlite:///test.db"
    config_manager.set_db_url(test_db_url)
    print(f"2. Set database URL to: {test_db_url}")
    
    # Test setting table descriptions file
    test_desc_file = "/path/to/test_descriptions.json"
    config_manager.set_table_descriptions_file(test_desc_file)
    print(f"3. Set table descriptions file to: {test_desc_file}")
    
    # Test getting configuration
    config = config_manager.get_config()
    print(f"4. Retrieved full configuration: {config}")
    
    # Test getting specific values
    db_url = config_manager.get_db_url()
    desc_file = config_manager.get_table_descriptions_file()
    print(f"5. Retrieved database URL: {db_url}")
    print(f"6. Retrieved table descriptions file: {desc_file}")
    
    # Verify values match what we set
    assert db_url == test_db_url, f"Expected {test_db_url}, got {db_url}"
    assert desc_file == test_desc_file, f"Expected {test_desc_file}, got {desc_file}"
    print("7. Values match expected values ✓")
    
    # Save the configuration
    success = config_manager.save_config()
    print(f"8. Configuration saved: {success}")
    
    # Reset configuration
    config_manager.reset_config()
    reset_config = config_manager.get_config()
    print(f"9. After reset, configuration: {reset_config}")
    
    # Verify reset to defaults
    assert reset_config['db_url'] == '', f"Expected empty string after reset, got {reset_config['db_url']}"
    assert reset_config['table_descriptions_file'] == '', f"Expected empty string after reset, got {reset_config['table_descriptions_file']}"
    print("10. Configuration properly reset ✓")
    
    print("\nAll configuration tests passed! ✓")


if __name__ == "__main__":
    test_config()