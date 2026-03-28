"""
LedgerX API — Production FastAPI application.
Activates core/ with PostgreSQL, Redis, JWT auth.
"""
import sys
from pathlib import Path

# Add core/ to Python path so its bare imports (from config, from db, etc.) work
_core = Path(__file__).resolve().parent / "core"
if str(_core) not in sys.path:
    sys.path.insert(0, str(_core))

from dotenv import load_dotenv
load_dotenv()  # Load .env before anything else

from core.main import app  # noqa: E402, F401

# Re-export app so uvicorn main:app works
__all__ = ["app"]
