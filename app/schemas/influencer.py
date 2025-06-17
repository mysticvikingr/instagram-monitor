import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from app.db.enums import TaskStatusEnum
from app.schemas.enums import IntervalEnum
from enum import Enum


class CreateMonitorTaskRequest(BaseModel):
    username: str
    interval: IntervalEnum


class CreateMonitorTaskData(BaseModel):
    task_id: uuid.UUID
    username: str
    status: TaskStatusEnum
    interval_seconds: int


class InfluencerHistoryData(BaseModel):
    follower_count: int
    following_count: int
    post_count: int
    bio: str
    recorded_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True


class UserHistoryData(BaseModel):
    username: str
    history: List[InfluencerHistoryData]


class TaskData(BaseModel):
    task_id: uuid.UUID = Field(..., alias="id")
    username: str
    status: TaskStatusEnum
    interval_seconds: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        validate_by_name = True


class StopTasksRequest(BaseModel):
    task_ids: List[uuid.UUID]


class StopTasksData(BaseModel):
    deleted_task_ids: List[uuid.UUID]


class TaskStatusData(BaseModel):
    status: TaskStatusEnum


class TaskUpdateData(BaseModel):
    task_id: uuid.UUID
    status: TaskStatusEnum 