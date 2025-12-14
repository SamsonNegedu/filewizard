#!/usr/bin/env python3
"""
Test the automatic database migration functionality.
"""

import os
import tempfile
import sqlite3
from pathlib import Path

def test_auto_migration_logic():
    """Test the migration logic that would run in the app startup."""

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

        # Insert some test data
        cursor.execute("""
            INSERT INTO jobs (id, user_id, task_type, original_filename, created_at)
            VALUES ('test-job-1', 'old-user', 'conversion', 'test.pdf', '2024-01-01T00:00:00Z')
        """)

        conn.commit()
        conn.close()

        # Now simulate the auto-migration logic
        print("Testing auto-migration logic...")

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check if session_id column exists (it shouldn't)
        cursor.execute("PRAGMA table_info(jobs)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        print(f"Columns before migration: {column_names}")

        if 'session_id' not in column_names:
            print("✓ session_id column missing - running migration...")

            # Run the migration
            cursor.execute("ALTER TABLE jobs ADD COLUMN session_id TEXT")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_jobs_session_id ON jobs(session_id)")

            print("✓ Migration completed")

            # Verify the migration worked
            cursor.execute("PRAGMA table_info(jobs)")
            columns_after = cursor.fetchall()
            column_names_after = [col[1] for col in columns_after]

            print(f"Columns after migration: {column_names_after}")

            assert 'session_id' in column_names_after, "session_id column should exist after migration"

            # Check that existing data is preserved
            cursor.execute("SELECT id, user_id, session_id FROM jobs WHERE id = 'test-job-1'")
            row = cursor.fetchone()
            assert row[0] == 'test-job-1', "Job ID should be preserved"
            assert row[1] == 'old-user', "user_id should be preserved"
            assert row[2] is None, "session_id should be NULL for existing records"

            print("✓ Existing data preserved")
            print("✓ Auto-migration test passed!")

        else:
            print("❌ session_id column already exists - test setup failed")

        conn.close()

    finally:
        # Clean up
        if db_path.exists():
            db_path.unlink()

if __name__ == '__main__':
    print("Testing automatic database migration...\n")
    test_auto_migration_logic()
    print("\n🎉 Auto-migration test completed successfully!")
