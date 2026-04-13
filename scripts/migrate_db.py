"""
Automation script for running database migrations via Alembic.
Can be run manually or during CI/CD.
"""
import subprocess
import os
import asyncio
from alembic.config import Config
from alembic import command

def run_command(command_str: str):
    print(f"Executing: {command_str}")
    result = subprocess.run(command_str, shell=True)
    if result.returncode != 0:
        print(f"Error: Command failed with exit code {result.returncode}")

async def run_migrations_programmatically():
    """Run migrations within an async context (e.g. FastAPI lifespan)."""
    print("🚀 Running Database Migrations Programmatically...")
    loop = asyncio.get_event_loop()
    
    alembic_cfg = Config("alembic.ini")
    
    # Run in executor to avoid blocking the event loop
    await loop.run_in_executor(None, command.upgrade, alembic_cfg, "head")
    print("✅ Programmatic migrations complete.")

def main():
    # Set PYTHONPATH so alembic can find src
    os.environ["PYTHONPATH"] = os.path.join(os.getcwd(), "src")

    print("🚀 Initializing Database Migrations...")
    
    # Check if migrations directory has any versions
    versions_dir = "src/database/migrations/versions"
    if not os.path.exists(versions_dir) or not os.listdir(versions_dir):
        print("Empty migration folder. Generating initial migration...")
        run_command("alembic revision --autogenerate -m 'Initial production schema'")
    
    print("Running migration upgrade head...")
    run_command("alembic upgrade head")
    
    print("\n✅ Migration process complete.")

if __name__ == "__main__":
    main()
