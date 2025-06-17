import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.services.post import PostService, get_post_service, extract_post_code
from app.schemas.post import (
    CreatePostMonitorTaskRequest,
    CreatePostMonitorTaskData,
    VideoHistoryData,
    PostTaskData,
    StopPostTasksRequest,
    StopPostTasksData,
    PostTaskStatusData,
    PostTaskUpdateData,
)
from app.schemas.response import Response
from app.db.enums import TaskStatusEnum

router = APIRouter()


@router.post("/create_monitor_task", status_code=status.HTTP_201_CREATED, response_model=Response[CreatePostMonitorTaskData])
def create_monitor_task(
    task_data: CreatePostMonitorTaskRequest,
    service: PostService = Depends(get_post_service),
):
    """
    Start tracking a given post.
    """
    post_code = extract_post_code(str(task_data.post_url))
    if not post_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Instagram post URL")
    
    if service.get_task_by_post_code(post_code):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Task with this post code already exists")

    task = service.create_monitor_task(task_data, post_code)
    return Response(
        status_code=status.HTTP_201_CREATED,
        data=CreatePostMonitorTaskData(
            task_id=uuid.UUID(task.id),
            post_code=task.post_code,
            status=task.status,
            interval_seconds=task.interval_seconds,
        ),
    )


@router.get("/video_history/{post_code}", response_model=Response[VideoHistoryData])
async def get_video_history(
    post_code: str,
    service: PostService = Depends(get_post_service),
):
    """
    Retrieve historical engagement data for the post.
    """
    history = await service.get_video_history(post_code)
    return Response(data=VideoHistoryData(post_code=post_code, history=history))


@router.get("/tasks", response_model=Response[List[PostTaskData]])
def list_tasks(service: PostService = Depends(get_post_service)):
    """
    List all post monitoring tasks.
    """
    tasks = service.list_tasks()
    return Response(data=tasks)


@router.post("/stop_tasks", response_model=Response[StopPostTasksData])
def stop_tasks(
    stop_request: StopPostTasksRequest,
    service: PostService = Depends(get_post_service),
):
    """
    Stop one or more post monitoring tasks.
    """
    task_ids_str = [str(tid) for tid in stop_request.task_ids]
    stopped_ids = service.stop_tasks(task_ids_str)
    stopped_ids_uuid = [uuid.UUID(sid) for sid in stopped_ids]
    return Response(data=StopPostTasksData(deleted_task_ids=stopped_ids_uuid))


@router.get("/task_status/{task_id}", response_model=Response[PostTaskStatusData])
def get_task_status(
    task_id: uuid.UUID,
    service: PostService = Depends(get_post_service),
):
    """
    Check the status of a post monitoring task.
    """
    task = service.get_task(str(task_id))
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return Response(data=PostTaskStatusData(status=task.status))


@router.post("/pause_task/{task_id}", response_model=Response[PostTaskUpdateData])
async def pause_task(
    task_id: uuid.UUID,
    service: PostService = Depends(get_post_service),
):
    """
    Pause tracking for a post.
    """
    task = await service.update_task_status(str(task_id), TaskStatusEnum.paused)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return Response(data=PostTaskUpdateData(task_id=uuid.UUID(task.id), status=task.status))


@router.post("/resume_task/{task_id}", response_model=Response[PostTaskUpdateData])
async def resume_task(
    task_id: uuid.UUID,
    service: PostService = Depends(get_post_service),
):
    """
    Resume tracking for a paused post task.
    """
    task = await service.update_task_status(str(task_id), TaskStatusEnum.active)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return Response(data=PostTaskUpdateData(task_id=uuid.UUID(task.id), status=task.status))
