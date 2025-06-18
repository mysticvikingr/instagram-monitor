import logging
import json
from app.db.session import SessionLocal
from app.db.redis import get_redis_client
from app.models.task import Task
from app.db.enums import TaskTypeEnum
from app.utils.tikhub import fetch_from_tikhub
from app.services.influencer import InfluencerService
from app.services.post import PostService
from sqlalchemy.orm import Session
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

async def _update_history(task: Task, data: dict, db: Session, redis_client: Redis):
    """Updates the metrics history for a task and invalidates relevant caches."""
    if task.task_type == TaskTypeEnum.influencer:
        influencerService = InfluencerService(db, redis_client)
        await influencerService.create_metrics_history(task.username, data)
    elif task.task_type == TaskTypeEnum.post:
        postService = PostService(db, redis_client)
        await postService.create_metrics_history(task.post_code, data)
    logger.info(f"Updated DB and cleared cache for task {task.id}")


async def process_task_by_id(task_id: str):
    db = SessionLocal()
    redis_client = await get_redis_client()
    metrics_data = None
    
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.warning(f"Task with id {task_id} not found.")
            return

        # Determine API endpoint and parameters
        endpoint = ""
        params = {}
        if task.task_type == TaskTypeEnum.influencer:
            endpoint = "/fetch_user_info_by_username_v2"
            params = {"username": task.username}
        elif task.task_type == TaskTypeEnum.post:
            endpoint = "/fetch_post_details_by_url"
            params = {"url": f"https://www.instagram.com/p/{task.post_code}/"}

        # Attempt to fetch live data from the API
        api_response = await fetch_from_tikhub(endpoint, params)
        fallback_key = f"fallback:{task.id}"
        
        if api_response and api_response.get("data"):
            logger.info(f"Successfully fetched data for task {task.id}")
            metrics_data = api_response["data"]
            # For post tasks, the metrics are nested deeper
            if task.task_type == TaskTypeEnum.post and "data" in metrics_data and "metrics" in metrics_data["data"]:
                 metrics_data = metrics_data["data"]["metrics"]
            
            # Store successful response in Redis as a fallback
            await redis_client.set(fallback_key, json.dumps(metrics_data), ex=3 * task.interval_seconds)
        else:
            logger.warning(f"Failed to fetch data for task {task.id} from API. Checking fallback.")
            fallback_data = await redis_client.get(fallback_key)
            if fallback_data:
                logger.info(f"Found fallback data for task {task.id}.")
                metrics_data = json.loads(fallback_data)
            else:
                logger.error(f"No fallback data available for task {task.id}.")

        # If we have metrics (from API or fallback), update the history
        if metrics_data:
            await _update_history(task, metrics_data, db, redis_client)

    except Exception as e:
        logger.error(f"An unexpected error occurred while processing task {task_id}: {e}", exc_info=True)
    finally:
        db.close()
        await redis_client.close() 