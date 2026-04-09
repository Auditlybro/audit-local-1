import asyncio
import sys
import os

# Add the current directory to sys.path to ensure core imports work
sys.path.append(os.getcwd())

from core.db.database import SessionLocal
from core.models.organization import ActivityLog
from sqlalchemy import select

async def main():
    print("--- LATEST ACTIVITY LOGS ---")
    async with SessionLocal() as db:
        try:
            stmt = select(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(10)
            result = await db.execute(stmt)
            logs = result.scalars().all()
            
            if not logs:
                print("No logs found in the database yet.")
                return

            for l in logs:
                print(f"[{l.created_at}] Action: {l.action} | Entity: {l.entity_type}")
                print(f"   Metadata: {l.metadata_json}")
                print("-" * 30)
        except Exception as e:
            print(f"Error querying database: {e}")

if __name__ == "__main__":
    asyncio.run(main())
