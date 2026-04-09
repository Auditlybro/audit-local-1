import asyncio
import sys
import os

# Add core to sys.path
sys.path.append(os.path.join(os.getcwd(), "core"))

from sqlalchemy import text
from db.database import engine

async def check():
    async with engine.connect() as conn:
        print("Checking tables...")
        # Check if username exists in users
        try:
            res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'username'"))
            exists = res.fetchone()
            if not exists:
                print("Adding 'username' column to 'users' table...")
                await conn.execute(text("ALTER TABLE users ADD COLUMN username VARCHAR(50) UNIQUE"))
                await conn.commit()
                print("Column 'username' added successfully.")
            else:
                print("Column 'username' already exists.")
        except Exception as e:
            print(f"Error checking/altering table: {e}")

if __name__ == "__main__":
    asyncio.run(check())
