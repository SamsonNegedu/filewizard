#!/usr/bin/env python3
"""
Database migration script to add session_id column to existing Job tables.

NOTE: This script is primarily for manual migrations. The application will
automatically run this migration on startup when SESSION_BASED_SCOPING=True.

Use this script only if:
- You want to migrate manually before enabling session scoping
- The automatic migration fails for some reason
- You're running in an environment where auto-migration is disabled
"""

import os
import sqlite3
from pathlib import Path

def migrate_database():
    """Add session_id column to existing jobs table if it doesn't exist."""

    # Database path (same as in main.py)
    db_path = Path(__file__).parent / "jobs.db"

    if not db_path.exists():
        print("No existing database found. Migration not needed.")
        return

    print(f"Migrating database at: {db_path}")

    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Check if session_id column already exists
        cursor.execute("PRAGMA table_info(jobs)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'session_id' in column_names:
            print("✓ session_id column already exists. No migration needed.")
            return

        print("Adding session_id column to jobs table...")

        # Add the session_id column
        cursor.execute("ALTER TABLE jobs ADD COLUMN session_id TEXT")

        # Create index on session_id for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_jobs_session_id ON jobs(session_id)")

        # Commit the changes
        conn.commit()

        print("✓ Migration completed successfully!")
        print("  - Added session_id column to jobs table")
        print("  - Created index on session_id for performance")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def main():
    print("FileWizard Session Scoping Database Migration")
    print("=" * 50)

    # Check for non-interactive flag
    import sys
    force = '--force' in sys.argv or os.getenv('MIGRATE_FORCE', '').lower() in ('true', '1', 'yes')

    if not force:
        # Confirm before proceeding
        try:
            response = input("This will modify your jobs.db file. Continue? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("Migration cancelled.")
                return 0
        except EOFError:
            # Non-interactive environment (like Docker)
            print("Non-interactive environment detected. Use --force or MIGRATE_FORCE=true to proceed.")
            print("Migration cancelled.")
            return 0

    try:
        migrate_database()
        print("\n🎉 Migration completed! You can now enable SESSION_BASED_SCOPING=True")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("Please backup your jobs.db file and try again, or delete it to start fresh.")
        return 1

    return 0

if __name__ == '__main__':
    exit(main())
