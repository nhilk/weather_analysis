from celery import Celery
from celery.schedules import crontab
import logging
import sys, os


logger = logging.getLogger(__name__)
logging.basicConfig(filename="log/weather_analysis.log", level=logging.INFO,)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from db import DB

celery_app = Celery(
    "src.dashboard",
    broker=os.getenv('CELERY_BROKER_URL'),
    backend=os.getenv('CELERY_RESULT_BACKEND'),
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_time_limit=3000,    
    task_soft_time_limit=240,
    result_expires=3600,
    # Persist Beat's schedule file so restarts don't re-run immediately due to lost state
    beat_schedule_filename="/weather_analysis/celerybeat-schedule",
    # Import modules if needed for task discovery (avoid importing Dash app in workers)
    include=["src.db"],
)

# Define the task at module level so workers can execute it without any Beat-only hooks
@celery_app.task(
    name="weather.run_weather_download",
    ignore_result=True,
    store_errors_even_if_ignored=False,
)
def run_weather_download_task(num_reads: int = 1, location_id: int = 1):
    import src.ambient_weather as ambient_weather
    return ambient_weather.run_weather_download(num_reads=num_reads, location_id=location_id)

# Configure Beat schedule statically; Beat will honor this, workers will ignore it
celery_app.conf.beat_schedule = {
    "ambient-weather-download-every-3h": {
        "task": "weather.run_weather_download",
        "schedule": crontab(minute="2", hour="*/3"),
        "args": (1, 1),
    }
}