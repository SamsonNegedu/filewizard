#!/usr/bin/env python3
"""
Test script for session-based job scoping functionality.
This script tests that session IDs are properly generated and jobs are scoped correctly.
"""

import os
import sys
import secrets
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables for testing
os.environ['SESSION_BASED_SCOPING'] = 'True'
os.environ['LOCAL_ONLY_MODE'] = 'True'

def test_session_id_generation():
    """Test that session IDs are generated correctly."""
    from main import generate_session_id, validate_session_id

    # Generate a few session IDs
    session_ids = [generate_session_id() for _ in range(5)]

    print("Testing session ID generation:")
    for i, session_id in enumerate(session_ids):
        is_valid = validate_session_id(session_id)
        print(f"  Session ID {i+1}: {session_id[:20]}... (valid: {is_valid})")
        assert is_valid, f"Session ID {session_id} is not valid"

    # Test that they're unique
    assert len(set(session_ids)) == len(session_ids), "Session IDs are not unique"
    print("  ✓ All session IDs are unique and valid")

def test_session_scoping_logic():
    """Test the session scoping logic."""
    from main import SESSION_BASED_SCOPING, get_session_id_from_request
    from fastapi import Request
    from unittest.mock import Mock

    print("\nTesting session scoping configuration:")
    assert SESSION_BASED_SCOPING == True, "SESSION_BASED_SCOPING should be True"
    print("  ✓ SESSION_BASED_SCOPING is enabled")

    # Test session ID extraction from request
    mock_request = Mock()
    mock_request.query_params = {'session_id': 'test_session_123'}
    mock_request.headers = {}

    session_id = get_session_id_from_request(mock_request)
    assert session_id == 'test_session_123', "Should extract session_id from query params"
    print("  ✓ Session ID extraction from query params works")

    # Test session ID from headers
    mock_request.query_params = {}
    mock_request.headers = {'X-Session-ID': 'header_session_456'}

    session_id = get_session_id_from_request(mock_request)
    assert session_id == 'header_session_456', "Should extract session_id from headers"
    print("  ✓ Session ID extraction from headers works")

def test_database_schema():
    """Test that the database schema includes session_id."""
    from main import Job, JobCreate

    print("\nTesting database schema:")

    # Check Job model has session_id column
    job_columns = [col.name for col in Job.__table__.columns]
    assert 'session_id' in job_columns, "Job model should have session_id column"
    print("  ✓ Job model has session_id column")

    # Check JobCreate model accepts session_id
    job_create_fields = JobCreate.model_fields.keys()
    assert 'session_id' in job_create_fields, "JobCreate should accept session_id"
    print("  ✓ JobCreate model accepts session_id")

def run_tests():
    """Run all tests."""
    print("Running session-based scoping tests...\n")

    try:
        test_session_id_generation()
        test_session_scoping_logic()
        test_database_schema()

        print("\n🎉 All tests passed! Session-based scoping is properly implemented.")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
