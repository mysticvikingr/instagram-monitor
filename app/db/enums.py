# app/db/enums.py
import enum

class TaskTypeEnum(str, enum.Enum):
    influencer = "influencer"
    post = "post"

class TaskStatusEnum(str, enum.Enum):
    active = "active"
    paused = "paused"
    stopped = "stopped"
