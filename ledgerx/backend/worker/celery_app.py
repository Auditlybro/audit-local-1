"""
Celery app for LedgerX background tasks.
Broker: Redis (default). Progress stored in Redis: task:{task_id}:progress, task:{task_id}:status.
"""
from celery import Celery
import os

broker = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

app = Celery(
    "ledgerx",
    broker=broker,
    backend=backend,
    include=["worker.tasks"],
)
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
)
