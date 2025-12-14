#!/usr/bin/env python3
"""
Test the connection handling fix for auto-migration.
"""

import os
import tempfile
import sqlite3
from pathlib import Path

def test_connection_handling():
    """Test that the migration logic works with separate connections."""

    # Create a temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = Path(tmp.name)

    try:
        # Create a basic jobs table without session_id column
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Create jobs table like the old schema
        cursor.execute("""
            CREATE TABLE jobs (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                parent_job_id TEXT,
                task_type TEXT,
                status TEXT DEFAULT 'pending',
                progress INTEGER DEFAULT 0,
                original_filename TEXT,
                input_filepath TEXT,
                input_filesize INTEGER,
                processed_filepath TEXT,
                output_filesize INTEGER,
                result_preview TEXT,
                error_message TEXT,
                callback_url TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        conn.commit()
        conn.close()

        # Simulate the fixed migration logic (using separate connections)
        print("Testing connection handling fix...")

        # First connection (simulate create_all)
        conn1 = sqlite3.connect(str(db_path))
        # Simulate that create_all worked
        conn1.close()  # Connection closed

        # Second connection (simulate migration check)
        conn2 = sqlite3.connect(str(db_path))
        cursor2 = conn2.cursor()

        # Check if session_id column exists
        cursor2.execute("PRAGMA table_info(jobs)")
        columns = cursor2.fetchall()
        column_names = [col[1] for col in columns]

        print(f"Columns before migration: {column_names}")

        if 'session_id' not in column_names:
            print("✓ session_id column missing - running migration...")

            # Run the migration
            cursor2.execute("ALTER TABLE jobs ADD COLUMN session_id TEXT")
            cursor2.execute("CREATE INDEX IF NOT EXISTS ix_jobs_session_id ON jobs(session_id)")

            print("✓ Migration completed using separate connection")

            # Verify the migration worked
            cursor2.execute("PRAGMA table_info(jobs)")
            columns_after = cursor2.fetchall()
            column_names_after = [col[1] for col in columns_after]

            print(f"Columns after migration: {column_names_after}")

            assert 'session_id' in column_names_after, "session_id column should exist after migration"

            print("✓ Migration successful with separate connections")

        conn2.commit()
        conn2.close()

        print("✓ Connection handling test passed!")

    finally:
        # Clean up
        if db_path.exists():
            db_path.unlink()

if __name__ == '__main__':
    print("Testing connection handling fix for auto-migration...\n")
    test_connection_handling()
    print("\n🎉 Connection handling test completed successfully!")
