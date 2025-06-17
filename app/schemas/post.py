import uuid
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from typing import List
from app.schemas.enums import IntervalEnum
from app.db.enums import TaskStatusEnum


class CreatePostMonitorTaskRequest(BaseModel):
    post_url: HttpUrl
    interval: IntervalEnum


class CreatePostMonitorTaskData(BaseModel):
    task_id: uuid.UUID
    post_code: str
    status: TaskStatusEnum
    interval_seconds: int


class PostHistoryData(BaseModel):
    like_count: int
    comment_count: int
    play_count: int
    recorded_at: datetime

    class Config:
        from_attributes = True


class VideoHistoryData(BaseModel):
    post_code: str
    history: List[PostHistoryData]


class PostTaskData(BaseModel):
    task_id: uuid.UUID = Field(..., alias="id")
    post_code: str
    status: TaskStatusEnum
    interval_seconds: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class StopPostTasksRequest(BaseModel):
    task_ids: List[uuid.UUID]


class StopPostTasksData(BaseModel):
    deleted_task_ids: List[uuid.UUID]


class PostTaskStatusData(BaseModel):
    status: TaskStatusEnum


class PostTaskUpdateData(BaseModel):
    task_id: uuid.UUID
    status: TaskStatusEnum 