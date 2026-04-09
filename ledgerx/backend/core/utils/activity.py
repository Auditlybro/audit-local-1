import logging
from uuid import UUID
from datetime import datetime
from typing import Any, Dict, Optional, Union

from db.database import AsyncSessionLocal
from models import ActivityLog

# Set up integrated loggers
logger = logging.getLogger("ledgerx.activity")

async def log_activity_background(
    company_id: Optional[UUID],
    user_id: Optional[UUID],
    action: str,
    description: str,
    metadata_json: Optional[Union[Dict[str, Any], list]] = None
):
    """
    Background worker that records an activity log entry.
    Uses its own DB session to ensure isolation from the main request.
    Wraps everything in a global try/except safety net.
    """
    try:
        async with AsyncSessionLocal() as db:
            log_entry = ActivityLog(
                company_id=company_id,
                user_id=user_id,
                action=action,
                description=description,
                metadata_json=metadata_json or {}
            )
            db.add(log_entry)
            await db.commit()
            # No need to flush or refresh since this is a fire-and-forget background task
    except Exception as e:
        # We log the error locally so it doesn't crash the main app flow
        logger.error(f"BACKGROUND LOGGING ERROR: {str(e)}", exc_info=True)
        print(f"BACKGROUND LOGGING ERROR: {str(e)}")

# Compatibility alias to prevent backend crashes during transition
log_activity = log_activity_background
