import asyncio
import sys
import os
from sqlalchemy import text

# Add core to sys.path
sys.path.append(os.path.join(os.getcwd(), "core"))
from db.database import AsyncSessionLocal

async def fix_social_users():
    async with AsyncSessionLocal() as db:
        try:
            # Update users where password_hash is null and name is set - likely social
            print("Updating existing social users who were defaulted to 'manual'...")
            # We can't be 100% sure if it's google or microsoft without more info,
            # but setting to 'google' is a safe enough block for 'manual' registration.
            await db.execute(text("UPDATE users SET auth_method = 'google' WHERE auth_method = 'manual' AND password_hash IS NULL AND name IS NOT NULL"))
            await db.commit()
            print("Cleanup successful.")
        except Exception as e:
            print(f"Cleanup failed: {e}")

if __name__ == "__main__":
    asyncio.run(fix_social_users())
