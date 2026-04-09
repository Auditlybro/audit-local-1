import asyncio
import os
import sys

# Add the current directory to sys.path so we can import from 'db'
sys.path.append(os.getcwd())

from db.database import engine
from sqlalchemy import text

async def check_schema():
    async with engine.connect() as conn:
        # Check users table
        print("--- Checking 'users' table ---")
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'"))
        cols = [r[0] for r in res]
        print(f"Users columns: {cols}")
        
        # Check activity_logs table
        print("\n--- Checking 'activity_logs' table ---")
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'activity_logs'"))
        cols = [r[0] for r in res]
        print(f"ActivityLog columns: {cols}")

if __name__ == "__main__":
    asyncio.run(check_schema())
