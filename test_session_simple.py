#!/usr/bin/env python3
"""
Simple test for session utilities without importing the full application.
"""

import secrets
import os

def generate_session_id() -> str:
    """Generate a secure random session ID."""
    return secrets.token_urlsafe(32)

def validate_session_id(session_id: str) -> bool:
    """Validate session ID format and length."""
    if not session_id:
        return False
    # Basic validation - should be URL-safe base64, ~43 characters
    return len(session_id) >= 32 and session_id.replace('-', '').replace('_', '').isalnum()

def test_session_generation():
    """Test session ID generation and validation."""
    print("Testing session ID generation:")

    # Generate multiple session IDs
    session_ids = [generate_session_id() for _ in range(5)]

    for i, session_id in enumerate(session_ids, 1):
        is_valid = validate_session_id(session_id)
        print(f"  Session ID {i}: {session_id[:20]}... (valid: {is_valid})")
        assert is_valid, f"Session ID should be valid"

    # Check uniqueness
    assert len(set(session_ids)) == len(session_ids), "Session IDs should be unique"
    print("  ✓ All session IDs are valid and unique")

    # Test invalid session IDs
    invalid_ids = ["", "short", "invalid@chars!", "spaces not allowed"]
    for invalid_id in invalid_ids:
        assert not validate_session_id(invalid_id), f"Invalid ID '{invalid_id}' should not validate"
    print("  ✓ Invalid session IDs are properly rejected")

def test_environment_flag():
    """Test environment flag parsing."""
    print("\nTesting environment flag:")

    # Test True values
    for value in ['True', 'true', '1', 't', 'T']:
        result = value.lower() in ('true', '1', 't')
        assert result == True, f"'{value}' should parse as True"
    print("  ✓ True values parse correctly")

    # Test False values
    for value in ['False', 'false', '0', 'f', 'F', 'anything_else']:
        result = value.lower() in ('true', '1', 't')
        assert result == False, f"'{value}' should parse as False"
    print("  ✓ False values parse correctly")

if __name__ == '__main__':
    print("Running simple session tests...\n")
    test_session_generation()
    test_environment_flag()
    print("\n🎉 All tests passed!")
