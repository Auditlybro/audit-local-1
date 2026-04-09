import asyncio
import sys
import os
from sqlalchemy import text

# Add core to sys.path
sys.path.append(os.path.join(os.getcwd(), "core"))
from db.database import AsyncSessionLocal

async def migrate():
    async with AsyncSessionLocal() as db:
        try:
            # Check if column exists
            result = await db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='auth_method'"))
            if not result.fetchone():
                print("Adding auth_method column to users table...")
                await db.execute(text("ALTER TABLE users ADD COLUMN auth_method VARCHAR(50) NOT NULL DEFAULT 'manual'"))
                await db.commit()
                print("Migration successful.")
            else:
                print("Column auth_method already exists.")
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    asyncio.run(migrate())
