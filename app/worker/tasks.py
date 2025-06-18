import asyncio
from app.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.task import Task
from app.db.enums import TaskStatusEnum
import logging
from app.worker.processing import process_task_by_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task
async def process_task(task_id: str):
    """
    Celery task to process a single monitoring task.
    It calls the asynchronous processing logic.
    """
    logger.info(f"Starting processing for task: {task_id}")
    await process_task_by_id(task_id)
    logger.info(f"Finished processing for task: {task_id}")


@celery_app.task
def retrieve_scheduled_tasks(interval_seconds: int):
    logger.info(f"Retrieving tasks with interval: {interval_seconds} seconds")
    db = SessionLocal()
    try:
        tasks = db.query(Task).filter(
            Task.interval_seconds == interval_seconds,
            Task.status == TaskStatusEnum.active
        ).all()

        logger.info(f"Found {len(tasks)} tasks to run for interval {interval_seconds}s.")

        for task in tasks:
            process_task.delay(task_id=task.id)
            
    except Exception as e:
        logger.error(f"Error retrieving scheduled tasks: {e}", exc_info=True)
    finally:
        db.close() 