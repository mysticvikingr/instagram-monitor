from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "Celery Scheduler",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    # backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)

celery_app.conf.beat_schedule = {
    "retrieve-scheduled-tasks-30-seconds": {
        "task": "app.worker.tasks.retrieve_scheduled_tasks",
        "schedule": 30.0,
        "args": (30,),
    },
    "retrieve-scheduled-tasks-30-minutes": {
        "task": "app.worker.tasks.retrieve_scheduled_tasks",
        "schedule": 1800.0,
        "args": (1800,),
    },
    "retrieve-scheduled-tasks-1-hour": {
        "task": "app.worker.tasks.retrieve_scheduled_tasks",
        "schedule": 3600.0,
        "args": (3600,),
    },
    "retrieve-scheduled-tasks-1-day": {
        "task": "app.worker.tasks.retrieve_scheduled_tasks",
        "schedule": 86400.0,
        "args": (86400,),
    },
    "retrieve-scheduled-tasks-7-days": {
        "task": "app.worker.tasks.retrieve_scheduled_tasks",
        "schedule": 604800.0,
        "args": (604800,),
    },
}