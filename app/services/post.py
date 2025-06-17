import uuid
import json
from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.dependencies import get_db
from app.db.redis import get_redis_client
from app.models.task import Task
from app.models.post_metrics_history import PostMetricsHistory
from app.schemas.post import CreatePostMonitorTaskRequest
from app.schemas.enums import INTERVAL_MAP
from app.db.enums import TaskTypeEnum, TaskStatusEnum
from app.utils.common import extract_post_code
from redis.asyncio import Redis


class PostService:
    def __init__(self, db: Session, redis_client: Redis):
        self.db = db
        self.redis_client = redis_client

    def get_task_by_post_code(self, post_code: str) -> Task:
        return self.db.query(Task).filter(Task.post_code == post_code, Task.task_type == TaskTypeEnum.post).first()

    def create_monitor_task(self, task_data: CreatePostMonitorTaskRequest, post_code: str) -> Task:
        interval_seconds = INTERVAL_MAP[task_data.interval]
        new_task = Task(
            id=str(uuid.uuid4()),
            task_type=TaskTypeEnum.post,
            post_code=post_code,
            interval_seconds=interval_seconds,
            status=TaskStatusEnum.active,
        )
        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)
        return new_task

    async def get_video_history(self, post_code: str) -> List[PostMetricsHistory]:
        cache_key = f"post_history:{post_code}"
        print(f"cache_key: {cache_key}")
        cached_history = await self.redis_client.get(cache_key)
        print(f"cached_history: {cached_history}")
        if cached_history:
            history_data = json.loads(cached_history)
            return [PostMetricsHistory(**item) for item in history_data]

        post_history = self.db.query(PostMetricsHistory).filter(PostMetricsHistory.post_code == post_code).order_by(PostMetricsHistory.recorded_at.desc()).all()
        print(f"post_history: {post_history}")
        if post_history:
            task = self.get_task_by_post_code(post_code)
            if task and task.interval_seconds > 0:
                history_to_cache = []
                for h in post_history:
                    h_dict = h.__dict__
                    h_dict.pop('_sa_instance_state', None)
                    h_dict['recorded_at'] = h.recorded_at.isoformat() if h.recorded_at else None
                    history_to_cache.append(h_dict)
                
                await self.redis_client.set(cache_key, json.dumps(history_to_cache), ex=task.interval_seconds)

        return post_history

    def list_tasks(self) -> List[Task]:
        return self.db.query(Task).filter(Task.task_type == TaskTypeEnum.post).all()

    def stop_tasks(self, task_ids: List[str]) -> List[str]:
        self.db.query(Task).filter(Task.id.in_(task_ids)).update({"status": TaskStatusEnum.stopped}, synchronize_session=False)
        self.db.commit()
        return task_ids

    def get_task(self, task_id: str) -> Task:
        return self.db.query(Task).filter(Task.id == task_id).first()

    async def update_task_status(self, task_id: str, status: TaskStatusEnum) -> Task:
        task = self.get_task(task_id)
        if task:
            if status == TaskStatusEnum.paused:
                await self.redis_client.set(f"paused_task:{task_id}", 1)
            elif status == TaskStatusEnum.active:
                await self.redis_client.delete(f"paused_task:{task_id}")

            task.status = status
            self.db.commit()
            self.db.refresh(task)
        return task


async def get_post_service(
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis_client)
) -> PostService:
    return PostService(db, redis_client) 