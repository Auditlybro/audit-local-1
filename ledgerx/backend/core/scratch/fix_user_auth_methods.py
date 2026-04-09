import asyncio
import os
import sys

sys.path.append(os.getcwd())

from db.database import engine
from sqlalchemy import text

async def check_and_fix_users():
    async with engine.connect() as conn:
        print("--- Checking for NULL auth_method values ---")
        res = await conn.execute(text("SELECT id, email, auth_method FROM users WHERE auth_method IS NULL"))
        null_users = [r for r in res]
        print(f"Found {len(null_users)} users with NULL auth_method.")
        
        if len(null_users) > 0:
            print("Fixing NULL auth_method values to 'manual'...")
            await conn.execute(text("UPDATE users SET auth_method = 'manual' WHERE auth_method IS NULL"))
            await conn.commit()
            print("Update complete.")
        else:
            print("No NULL auth_method values found. The issue might be elsewhere.")

if __name__ == "__main__":
    asyncio.run(check_and_fix_users())
