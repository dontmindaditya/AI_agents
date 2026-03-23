"""
Database Migration Management

This module provides CLI commands for managing database migrations.

Usage:
    from database.migrations import run_migrations, create_migration, rollback_migration
    
    # Run all pending migrations
    await run_migrations()
    
    # Rollback last migration
    await rollback_migration()
"""

import subprocess
import sys
from typing import Optional
from pathlib import Path


def run_migrations() -> bool:
    """
    Run all pending Alembic migrations.
    
    Returns:
        bool: True if migrations succeeded, False otherwise
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Migrations completed successfully:")
            print(result.stdout)
            return True
        else:
            print("Migration failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"Error running migrations: {e}")
        return False


def create_migration(message: str) -> Optional[str]:
    """
    Create a new Alembic migration.
    
    Args:
        message: Description of the migration
        
    Returns:
        str: Migration filename if successful, None otherwise
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", message],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Migration created:")
            print(result.stdout)
            return result.stdout.strip()
        else:
            print("Failed to create migration:")
            print(result.stderr)
            return None
            
    except Exception as e:
        print(f"Error creating migration: {e}")
        return None


def rollback_migration(steps: int = 1) -> bool:
    """
    Rollback migrations.
    
    Args:
        steps: Number of migrations to rollback (default: 1)
        
    Returns:
        bool: True if rollback succeeded, False otherwise
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "downgrade", f"-{steps}"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Rollback completed:")
            print(result.stdout)
            return True
        else:
            print("Rollback failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"Error rolling back migration: {e}")
        return False


def show_current_version() -> Optional[str]:
    """
    Show the current migration version.
    
    Returns:
        str: Current version or None
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "current"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            return version if version else None
        return None
        
    except Exception as e:
        print(f"Error getting current version: {e}")
        return None


def show_history() -> list:
    """
    Show migration history.
    
    Returns:
        list: List of migration info
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "history", "--verbose"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return result.stdout.strip().split('\n')
        return []
        
    except Exception as e:
        print(f"Error getting history: {e}")
        return []


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Migration Management")
    parser.add_argument("command", choices=["upgrade", "downgrade", "create", "history", "current"],
                        help="Command to run")
    parser.add_argument("-m", "--message", help="Migration message (for create)")
    parser.add_argument("-s", "--steps", type=int, default=1, help="Steps to rollback (for downgrade)")
    
    args = parser.parse_args()
    
    if args.command == "upgrade":
        success = run_migrations()
        sys.exit(0 if success else 1)
    elif args.command == "downgrade":
        success = rollback_migration(args.steps)
        sys.exit(0 if success else 1)
    elif args.command == "create":
        if not args.message:
            print("Error: -m/--message required for create")
            sys.exit(1)
        result = create_migration(args.message)
        sys.exit(0 if result else 1)
    elif args.command == "history":
        for line in show_history():
            print(line)
    elif args.command == "current":
        version = show_current_version()
        print(f"Current version: {version or 'None'}")
