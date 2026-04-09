import asyncio
from db.database import engine
from sqlalchemy import text

async def migrate():
    print("Starting migration: making activity_logs.company_id nullable...")
    try:
        async with engine.connect() as conn:
            await conn.execute(text('ALTER TABLE activity_logs ALTER COLUMN company_id DROP NOT NULL'))
            await conn.commit()
            print("Migration success: activity_logs.company_id is now nullable")
    except Exception as e:
        print(f"Migration error (this is okay if it's already nullable): {e}")

if __name__ == "__main__":
    asyncio.run(migrate())
