import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.services.influencer import InfluencerService, get_influencer_service
from app.schemas.influencer import (
    CreateMonitorTaskRequest,
    CreateMonitorTaskData,
    UserHistoryData,
    TaskData,
    StopTasksRequest,
    StopTasksData,
    TaskStatusData,
    TaskUpdateData,
)
from app.schemas.response import Response
from app.db.enums import TaskStatusEnum

router = APIRouter()

@router.post("/create_monitor_task", status_code=status.HTTP_201_CREATED, response_model=Response[CreateMonitorTaskData])
def create_monitor_task(
    task_data: CreateMonitorTaskRequest,
    service: InfluencerService = Depends(get_influencer_service),
):
    """
    Create a new influencer monitoring task.
    """
    if service.get_task_by_username(task_data.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Task with that username already exists")
    task = service.create_monitor_task(task_data)
    return Response(
        status_code=status.HTTP_201_CREATED,
        data=CreateMonitorTaskData(
            task_id=uuid.UUID(task.id),
            username=task.username,
            status=task.status,
            interval_seconds=task.interval_seconds,
        ),
    )

@router.get("/user_history/{username}", response_model=Response[UserHistoryData])
async def get_user_history(
    username: str,
    service: InfluencerService = Depends(get_influencer_service),
):
    """
    Retrieve historical data for a monitored user.
    """
    history = await service.get_user_history(username)
    return Response(data=UserHistoryData(username=username, history=history))

@router.get("/tasks", response_model=Response[List[TaskData]])
def list_tasks(service: InfluencerService = Depends(get_influencer_service)):
    """
    List all influencer monitoring tasks.
    """
    tasks = service.list_tasks()
    return Response(data=tasks)

@router.post("/stop_tasks", response_model=Response[StopTasksData])
def stop_tasks(
    stop_request: StopTasksRequest,
    service: InfluencerService = Depends(get_influencer_service),
):
    """
    Stop one or more monitoring tasks.
    """
    task_ids_str = [str(tid) for tid in stop_request.task_ids]
    stopped_ids = service.stop_tasks(task_ids_str)
    stopped_ids_uuid = [uuid.UUID(sid) for sid in stopped_ids]
    return Response(data=StopTasksData(deleted_task_ids=stopped_ids_uuid))

@router.get("/task_status/{task_id}", response_model=Response[TaskStatusData])
def get_task_status(
    task_id: uuid.UUID,
    service: InfluencerService = Depends(get_influencer_service),
):
    """
    Get status for a specific monitoring task.
    """
    task = service.get_task(str(task_id))
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return Response(data=TaskStatusData(status=task.status))

@router.post("/pause_task/{task_id}", response_model=Response[TaskUpdateData])
async def pause_task(
    task_id: uuid.UUID,
    service: InfluencerService = Depends(get_influencer_service),
):
    """
    Pause a monitoring task.
    """
    task = await service.update_task_status(str(task_id), TaskStatusEnum.paused)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return Response(data=TaskUpdateData(task_id=uuid.UUID(task.id), status=task.status))

@router.post("/resume_task/{task_id}", response_model=Response[TaskUpdateData])
async def resume_task(
    task_id: uuid.UUID,
    service: InfluencerService = Depends(get_influencer_service),
):
    """
    Resume a paused monitoring task.
    """
    task = await service.update_task_status(str(task_id), TaskStatusEnum.active)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return Response(data=TaskUpdateData(task_id=uuid.UUID(task.id), status=task.status))
