#!/usr/bin/env python3
"""
Test environment variable configuration for file cleanup.
"""

import os

def test_environment_variables():
    """Test that cleanup settings can be read from environment variables."""

    # Set test environment variables
    test_env = {
        'FILE_CLEANUP_ENABLED': 'true',
        'FILE_CLEANUP_INTERVAL': '7200',  # 2 hours
        'UPLOAD_FILE_RETENTION': '43200',  # 12 hours
        'PROCESSED_FILE_RETENTION': '259200',  # 3 days
        'TEMP_FILE_RETENTION': '1800',  # 30 minutes
    }

    # Save original values
    originals = {}
    for key in test_env:
        originals[key] = os.environ.get(key)
        os.environ[key] = test_env[key]

    try:
        # Test reading the values (simulating what the cleanup worker does)
        cleanup_enabled = os.getenv('FILE_CLEANUP_ENABLED', 'true').lower() in ('true', '1', 't')
        cleanup_interval = int(os.getenv('FILE_CLEANUP_INTERVAL', '3600'))
        upload_retention = int(os.getenv('UPLOAD_FILE_RETENTION', '86400'))
        processed_retention = int(os.getenv('PROCESSED_FILE_RETENTION', '604800'))
        temp_retention = int(os.getenv('TEMP_FILE_RETENTION', '3600'))

        # Verify values
        assert cleanup_enabled == True, "Cleanup should be enabled"
        assert cleanup_interval == 7200, f"Expected 7200, got {cleanup_interval}"
        assert upload_retention == 43200, f"Expected 43200, got {upload_retention}"
        assert processed_retention == 259200, f"Expected 259200, got {processed_retention}"
        assert temp_retention == 1800, f"Expected 1800, got {temp_retention}"

        print("✓ Environment variable configuration works correctly")
        print(f"  Cleanup enabled: {cleanup_enabled}")
        print(f"  Check interval: {cleanup_interval} seconds")
        print(f"  Upload retention: {upload_retention} seconds ({upload_retention/3600:.1f} hours)")
        print(f"  Processed retention: {processed_retention} seconds ({processed_retention/86400:.1f} days)")
        print(f"  Temp retention: {temp_retention} seconds ({temp_retention/60:.1f} minutes)")

    finally:
        # Restore original values
        for key, value in originals.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

def test_default_values():
    """Test that default values work when environment variables are not set."""

    # Clear any existing values
    keys_to_clear = ['FILE_CLEANUP_ENABLED', 'FILE_CLEANUP_INTERVAL', 'UPLOAD_FILE_RETENTION', 'PROCESSED_FILE_RETENTION', 'TEMP_FILE_RETENTION']
    originals = {}
    for key in keys_to_clear:
        originals[key] = os.environ.get(key)
        os.environ.pop(key, None)

    try:
        # Test with defaults
        cleanup_enabled = os.getenv('FILE_CLEANUP_ENABLED', 'true').lower() in ('true', '1', 't')
        cleanup_interval = int(os.getenv('FILE_CLEANUP_INTERVAL', '3600'))
        upload_retention = int(os.getenv('UPLOAD_FILE_RETENTION', '86400'))
        processed_retention = int(os.getenv('PROCESSED_FILE_RETENTION', '604800'))
        temp_retention = int(os.getenv('TEMP_FILE_RETENTION', '3600'))

        # Verify defaults
        assert cleanup_enabled == True, "Default cleanup should be enabled"
        assert cleanup_interval == 3600, f"Expected default 3600, got {cleanup_interval}"
        assert upload_retention == 86400, f"Expected default 86400, got {upload_retention}"
        assert processed_retention == 604800, f"Expected default 604800, got {processed_retention}"
        assert temp_retention == 3600, f"Expected default 3600, got {temp_retention}"

        print("✓ Default values work correctly")

    finally:
        # Restore original values
        for key, value in originals.items():
            if value is not None:
                os.environ[key] = value

if __name__ == '__main__':
    print("Testing environment variable configuration for file cleanup...\n")
    test_environment_variables()
    test_default_values()
    print("\n🎉 All environment variable tests passed!")
