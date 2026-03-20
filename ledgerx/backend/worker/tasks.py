"""
Celery tasks for LedgerX. Progress written to Redis: task:{task_id}:progress (0-100), task:{task_id}:status.
Frontend polls GET /tasks/{task_id}/status for real-time progress.
"""
import os
from worker.celery_app import app

REDIS_URL = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")


def _redis():
    import redis
    return redis.from_url(REDIS_URL)


def _set_progress(task_id: str, progress: int, status: str = "processing"):
    try:
        r = _redis()
        r.set(f"task:{task_id}:progress", min(100, max(0, progress)))
        r.set(f"task:{task_id}:status", status)
    except Exception:
        pass


@app.task(bind=True)
def import_tally_xml(self, file_path: str, company_id: str):
    """Long-running Tally XML import; update progress via Redis."""
    task_id = self.request.id
    _set_progress(task_id, 0, "started")
    try:
        # Placeholder: in production, call import_engine and parse file_path
        from core.utils.tally_parser import parse_tally_xml, parse_tally_masters
        from pathlib import Path
        path = Path(file_path)
        if not path.exists():
            _set_progress(task_id, 0, "failed")
            return {"ok": False, "error": "File not found"}
        content = path.read_text(encoding="utf-8", errors="replace")
        _set_progress(task_id, 20, "processing")
        masters = parse_tally_masters(content)
        vouchers = parse_tally_xml(content)
        _set_progress(task_id, 80, "processing")
        # Commit to DB would go here (company_id)
        _set_progress(task_id, 100, "completed")
        return {"ok": True, "masters": len(masters), "vouchers": len(vouchers)}
    except Exception as e:
        _set_progress(task_id, 0, "failed")
        return {"ok": False, "error": str(e)}


@app.task(bind=True)
def generate_gstr1(self, company_id: str, period: str):
    """Compute GSTR-1 JSON in background."""
    task_id = self.request.id
    _set_progress(task_id, 0, "started")
    try:
        # Placeholder: compute GSTR-1 from vouchers for period
        _set_progress(task_id, 50, "processing")
        _set_progress(task_id, 100, "completed")
        return {"ok": True, "company_id": company_id, "period": period}
    except Exception as e:
        _set_progress(task_id, 0, "failed")
        return {"ok": False, "error": str(e)}


@app.task(bind=True)
def run_ghost_analyst(self, company_id: str):
    """Run mismatch/duplicate/GST detection; store results."""
    task_id = self.request.id
    _set_progress(task_id, 0, "started")
    try:
        try:
            from ai.ghost_analyst import run_ghost_analyst
        except ImportError:
            from backend.ai.ghost_analyst import run_ghost_analyst
        _set_progress(task_id, 30, "processing")
        # In production: load vouchers + bank txns for company_id from DB
        result = run_ghost_analyst(vouchers=[], bank_transactions=[])
        _set_progress(task_id, 100, "completed")
        return {"ok": True, "risk_score": result.get("risk_score"), "summary": result.get("summary")}
    except Exception as e:
        _set_progress(task_id, 0, "failed")
        return {"ok": False, "error": str(e)}


@app.task(bind=True)
def send_invoice_whatsapp(self, voucher_id: str, phone: str):
    """WhatsApp Business API: send invoice to phone."""
    task_id = self.request.id
    _set_progress(task_id, 0, "started")
    try:
        # Placeholder: integrate WhatsApp Business API
        _set_progress(task_id, 100, "completed")
        return {"ok": True, "voucher_id": voucher_id, "phone": phone}
    except Exception as e:
        _set_progress(task_id, 0, "failed")
        return {"ok": False, "error": str(e)}


@app.task
def scheduled_gst_reminders():
    """Run daily: check filing deadlines, send alerts."""
    try:
        # Placeholder: load companies, check GSTR-1/3B due dates, send notifications
        return {"ok": True, "checked": 0}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# Task status for API: read from Redis
def get_task_status(task_id: str) -> dict:
    """Return { progress: 0-100, status: str } from Redis."""
    try:
        r = _redis()
        progress = r.get(f"task:{task_id}:progress")
        status = r.get(f"task:{task_id}:status")
        return {
            "task_id": task_id,
            "progress": int(progress) if progress else 0,
            "status": (status.decode("utf-8") if isinstance(status, bytes) else status) or "pending",
        }
    except Exception:
        return {"task_id": task_id, "progress": 0, "status": "unknown"}
