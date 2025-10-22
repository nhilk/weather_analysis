from celery import Celery
import os
print(os.getcwd())
celery_app = Celery(
    "src.dashboard",
    broker=os.getenv('CELERY_BROKER_URL'),
    backend=os.getenv('CELERY_RESULT_BACKEND'),
)

# Minimal recommended settings (JSON serialization)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    ask_time_limit=3000,        # hard limit (seconds) — worker kills the task forcibly
    task_soft_time_limit=240,   # soft limit — raises SoftTimeLimitExceeded in task
    result_expires=3600,
    # Import the dashboard module so background callbacks and tasks are registered
    include=["src.dashboard","src.db"],
)