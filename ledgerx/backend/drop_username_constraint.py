import asyncio
import sys
import os
from sqlalchemy import text

# Add core to sys.path
sys.path.append(os.path.join(os.getcwd(), "core"))
from db.database import engine

async def drop():
    async with engine.begin() as conn:
        print("Checking for unique constraints on 'users'...")
        # Find constraint names
        res = await conn.execute(text("""
            SELECT conname 
            FROM pg_constraint 
            WHERE conrelid = 'users'::regclass AND contype = 'u'
        """))
        constraints = [r[0] for r in res.fetchall()]
        print(f"Found constraints: {constraints}")
        
        for con in constraints:
            if 'username' in con:
                print(f"Dropping constraint: {con}")
                await conn.execute(text(f"ALTER TABLE users DROP CONSTRAINT IF EXISTS {con}"))
                print(f"Constraint {con} dropped.")
        
        # Also check for independent unique indexes that aren't constraints
        res = await conn.execute(text("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'users' AND indexdef LIKE '%username%' AND indexdef LIKE '%UNIQUE%'
        """))
        indexes = [r[0] for r in res.fetchall()]
        print(f"Found unique indexes: {indexes}")
        for idx in indexes:
            print(f"Dropping index: {idx}")
            await conn.execute(text(f"DROP INDEX IF EXISTS {idx}"))
            print(f"Index {idx} dropped.")

if __name__ == "__main__":
    asyncio.run(drop())
