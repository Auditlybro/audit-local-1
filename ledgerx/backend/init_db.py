"""
Initialize the LedgerX database — creates all tables.
Usage: python init_db.py
"""
import sys
import asyncio
from pathlib import Path

# Add core/ to Python path
_core = Path(__file__).resolve().parent / "core"
if str(_core) not in sys.path:
    sys.path.insert(0, str(_core))

from dotenv import load_dotenv
load_dotenv()

from db.database import engine, Base
# Import all models so they register with Base.metadata
import models  # noqa: F401


async def init():
    print(f"Connecting to: {engine.url}")
    async with engine.begin() as conn:
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
    print("Done! All tables created successfully.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init())
