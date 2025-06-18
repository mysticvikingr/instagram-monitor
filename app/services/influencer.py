import uuid
import json
from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.dependencies import get_db
from app.db.redis import get_redis_client
from app.models.task import Task
from app.models.influencer_metrics_history import InfluencerMetricsHistory
from app.schemas.influencer import CreateMonitorTaskRequest, UserHistoryData
from app.schemas.enums import INTERVAL_MAP
from app.db.enums import TaskTypeEnum, TaskStatusEnum
from redis.asyncio import Redis


class InfluencerService:
    def __init__(self, db: Session, redis_client: Redis):
        self.db = db
        self.redis_client = redis_client

    def get_task_by_username(self, username: str) -> Task:
        return self.db.query(Task).filter(Task.username == username, Task.task_type == TaskTypeEnum.influencer).first()

    def create_monitor_task(self, task_data: CreateMonitorTaskRequest) -> Task:
        existing_task = self.get_task_by_username(task_data.username)
        if existing_task:
            return None
            
        interval_seconds = INTERVAL_MAP[task_data.interval]
        new_task = Task(
            id=str(uuid.uuid4()),
            task_type=TaskTypeEnum.influencer,
            username=task_data.username,
            interval_seconds=interval_seconds,
            status=TaskStatusEnum.active,
        )
        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)
        return new_task

    async def create_metrics_history(self, username: str, metrics: dict):
        new_history = InfluencerMetricsHistory(
            username=username,
            user_id=int(metrics.get("id")),
            bio=metrics.get("biography"),
            follower_count=metrics.get("follower_count", 0),
            following_count=metrics.get("following_count", 0),
            post_count=metrics.get("media_count", 0)
        )
        self.db.add(new_history)
        self.db.commit()

        # Invalidate cache
        cache_key = f"user_history:{username}"
        await self.redis_client.delete(cache_key)

    async def get_user_history(self, username: str) -> List[InfluencerMetricsHistory]:
        cache_key = f"user_history:{username}"
        cached_history = await self.redis_client.get(cache_key)

        if cached_history:
            history_data = json.loads(cached_history)
            return [InfluencerMetricsHistory(**item) for item in history_data]

        user_history = self.db.query(InfluencerMetricsHistory).filter(InfluencerMetricsHistory.username == username).order_by(InfluencerMetricsHistory.recorded_at.desc()).all()
        
        if user_history:
            task = self.get_task_by_username(username)
            if task and task.interval_seconds > 0:
                history_to_cache = []
                for h in user_history:
                    h_dict = h.__dict__
                    h_dict.pop('_sa_instance_state', None)
                    h_dict['recorded_at'] = h.recorded_at.isoformat() if h.recorded_at else None
                    history_to_cache.append(h_dict)
                
                await self.redis_client.set(cache_key, json.dumps(history_to_cache), ex=task.interval_seconds)

        return user_history

    def list_tasks(self) -> List[Task]:
        return self.db.query(Task).filter(Task.task_type == TaskTypeEnum.influencer).all()

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


async def get_influencer_service(
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis_client)
) -> InfluencerService:
    return InfluencerService(db, redis_client) 