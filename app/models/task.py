from sqlalchemy import Column, String, Integer, Enum, DateTime, Index
from sqlalchemy.sql import func
from app.db.session import Base
from app.db.enums import TaskTypeEnum, TaskStatusEnum

class Task(Base):
    __tablename__ = "task"

    id = Column(String(36), primary_key=True)
    task_type = Column(Enum(TaskTypeEnum), nullable=False)
    username = Column(String(255), unique=True)
    post_code = Column(String(255), unique=True)
    interval_seconds = Column(Integer, nullable=False)
    status = Column(Enum(TaskStatusEnum), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_task_type", "task_type"),
        Index("ix_status", "status"),
    )
