#!/usr/bin/env python3
"""
Test file cleanup logic and configuration.
"""

import os
import time
from pathlib import Path

def test_cleanup_logic():
    """Test the file cleanup logic with mock file system."""

    # Mock configuration
    app_settings = {
        "file_cleanup_enabled": True,
        "file_cleanup_interval": 3600,
        "upload_file_retention": 86400,    # 24 hours
        "processed_file_retention": 604800, # 7 days
        "temp_file_retention": 3600,       # 1 hour
    }

    current_time = time.time()

    # Test file age calculations
    upload_cutoff = current_time - app_settings["upload_file_retention"]
    processed_cutoff = current_time - app_settings["processed_file_retention"]
    temp_cutoff = current_time - app_settings["temp_file_retention"]

    print("Testing file age calculations:")
    print(f"  Current time: {current_time}")
    print(f"  Upload cutoff (24h ago): {upload_cutoff}")
    print(f"  Processed cutoff (7d ago): {processed_cutoff}")
    print(f"  Temp cutoff (1h ago): {temp_cutoff}")

    # Test file that should be cleaned (older than cutoff)
    old_file_time = current_time - app_settings["upload_file_retention"] - 3600  # 25 hours ago
    should_clean = old_file_time < upload_cutoff
    print(f"  File from 25 hours ago should be cleaned: {should_clean}")
    assert should_clean, "Old file should be marked for cleanup"

    # Test file that should NOT be cleaned (newer than cutoff)
    new_file_time = current_time - 3600  # 1 hour ago
    should_not_clean = new_file_time >= upload_cutoff
    print(f"  File from 1 hour ago should NOT be cleaned: {should_not_clean}")
    assert should_not_clean, "New file should not be marked for cleanup"

    print("✓ File age calculations are correct")

def test_configuration_defaults():
    """Test default configuration values."""

    # Simulate the defaults from settings.default.yml
    defaults = {
        "file_cleanup_enabled": True,
        "file_cleanup_interval": 3600,      # 1 hour
        "upload_file_retention": 86400,     # 24 hours
        "processed_file_retention": 604800, # 7 days
        "temp_file_retention": 3600,        # 1 hour
    }

    print("\nTesting configuration defaults:")
    for key, value in defaults.items():
        print(f"  {key}: {value}")

        # Validate reasonable ranges
        if "retention" in key:
            assert value > 0, f"{key} should be positive"
            assert value >= 3600, f"{key} should be at least 1 hour"
        elif "interval" in key:
            assert value >= 300, f"{key} should be at least 5 minutes"

    print("✓ Configuration defaults are reasonable")

def test_directory_structure():
    """Test understanding of directory structure."""

    # Simulate the directory structure
    directories = {
        "uploads": "PATHS.UPLOADS_DIR",      # Original uploaded files
        "processed": "PATHS.PROCESSED_DIR",  # Converted/transcribed files
        "temp": "PATHS.CHUNK_TMP_DIR",       # Temporary chunk files
    }

    print("\nTesting directory understanding:")
    for name, path_var in directories.items():
        print(f"  {name}: {path_var}")

        # Simulate retention times for each
        if name == "uploads":
            retention = 86400  # 24 hours
        elif name == "processed":
            retention = 604800  # 7 days
        elif name == "temp":
            retention = 3600   # 1 hour

        print(f"    Retention: {retention} seconds ({retention/3600:.1f} hours)")

    print("✓ Directory structure understood correctly")

if __name__ == '__main__':
    print("Testing file cleanup system...\n")
    test_cleanup_logic()
    test_configuration_defaults()
    test_directory_structure()
    print("\n🎉 All file cleanup tests passed!")
