"""
GET /tasks/{task_id}/status — return progress and status from Redis for frontend progress bars.
"""
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_task_status(task_id: str) -> dict:
    try:
        from worker.tasks import get_task_status as _get
        return _get(task_id)
    except ImportError:
        try:
            import sys
            from pathlib import Path
            backend = Path(__file__).resolve().parent.parent.parent
            if str(backend) not in sys.path:
                sys.path.insert(0, str(backend))
            from worker.tasks import get_task_status as _get
            return _get(task_id)
        except Exception:
            return {"task_id": task_id, "progress": 0, "status": "unknown"}


@router.get("/{task_id}/status")
def get_task_status(task_id: str):
    """Return task progress (0-100) and status (pending|processing|completed|failed) from Redis."""
    if not task_id:
        raise HTTPException(status_code=400, detail="task_id required")
    return _get_task_status(task_id)
