from celery import Celery
import os
# Configure broker and result backend. Here we use Redis as an example.
# Broker (tasks queue): redis://localhost:6379/0
# Result backend (store task results): redis://localhost:6379/1
celery_app = Celery(
    "dashboard",
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
)