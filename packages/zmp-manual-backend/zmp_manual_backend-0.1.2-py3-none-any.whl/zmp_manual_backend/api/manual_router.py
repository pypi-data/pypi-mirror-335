from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Path as FastAPIPath,
    BackgroundTasks,
    Depends,
)
from sse_starlette.sse import EventSourceResponse
from zmp_manual_backend.core.manual_service import ManualService
from zmp_manual_backend.models.manual import (
    PublishRequest,
    PublishStatus,
    JobState,
    Notification,
    SolutionType,
    SidebarMenu,
    SidebarMenuItem,
)
from zmp_manual_backend.models.auth import TokenData
from zmp_manual_backend.api.auth_router import get_current_token_data
import asyncio
import os
from dotenv import load_dotenv
from typing import List, Optional
import logging
from pathlib import Path
import uuid

# Load environment variables from the project root directory
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"

# Parse VSCODE_ENV_REPLACE for environment variables
vscode_env = os.environ.get("VSCODE_ENV_REPLACE", "")
if vscode_env:
    # Split by : and parse each key=value pair
    env_pairs = vscode_env.split(":")
    for pair in env_pairs:
        if "=" in pair:
            key, value = pair.split("=", 1)
            # Only set if the value is not empty
            if value:
                os.environ[key] = value.replace("\\x3a", ":")  # Fix escaped colons

# Load .env file as fallback
load_dotenv(dotenv_path=env_path)

router = APIRouter()
logger = logging.getLogger("appLogger")


def initialize_manual_service() -> ManualService:
    """Initialize and return a ManualService instance."""
    try:
        notion_token = os.environ.get("NOTION_TOKEN")
        if not notion_token:
            logger.error("NOTION_TOKEN not found in environment variables")
            logger.error(f"Looking for .env file at: {env_path}")
            logger.error(f".env file exists: {env_path.exists()}")
            raise ValueError("NOTION_TOKEN environment variable is not set")

        logger.info(f"Initializing manual service with token: {notion_token[:5]}...")

        # Log the available root page IDs
        for solution in ["ZCP", "APIM", "AMDP"]:
            env_var = f"{solution}_ROOT_PAGE_ID"
            if os.environ.get(env_var):
                logger.info(f"Found {env_var} in environment variables")

        return ManualService(
            notion_token=notion_token,
            root_page_id=os.environ.get(
                "ZCP_ROOT_PAGE_ID"
            ),  # For backward compatibility
            repo_path=os.environ.get("REPO_BASE_PATH", "./repo"),
            source_dir=os.environ.get("SOURCE_DIR", "docs"),
            target_dir=os.environ.get("TARGET_DIR", "i18n"),
            github_repo_url=os.environ.get("GITHUB_REPO_URL"),
            target_languages=set(
                lang.strip()
                for lang in os.environ.get("TARGET_LANGUAGES", "ko,ja,zh").split(",")
            ),
        )
    except Exception as e:
        logger.error(f"Failed to initialize manual service: {str(e)}")
        raise


# Initialize service instance
manual_service = initialize_manual_service()


def get_manual_service() -> ManualService:
    """Dependency function to get the ManualService instance."""
    return manual_service


@router.get("/manuals")
async def get_manuals(
    selected_solution: SolutionType = Query(
        default=SolutionType.ZCP,
        description="The solution type to retrieve manuals for (zcp, apim, amdp)",
    ),
):
    """Get hierarchical list of manuals and folders for the specified solution"""
    try:
        items = await manual_service.get_manuals(selected_solution=selected_solution)

        # Convert Node objects to dictionaries
        items_dicts = []
        for item in items:
            item_dict = {
                "object_id": item.object_id,
                "title": item.name,
                "is_directory": item.is_directory,
                "parent_id": item.parent.object_id if item.parent else None,
                "notion_url": item.notion_url,
                "index": item.index,
            }
            items_dicts.append(item_dict)

        return {"items": items_dicts}
    except Exception as e:
        logger.error(f"Error getting manuals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/publish")
async def publish_manual(
    request: PublishRequest,
    background_tasks: BackgroundTasks,
    user_id: Optional[str] = Query(
        None, description="User ID for notification tracking"
    ),
    manual_service: ManualService = Depends(get_manual_service),
) -> dict:
    """Publish a manual by exporting it from Notion and translating it."""
    try:
        if not request.notion_page_id:
            raise HTTPException(status_code=400, detail="notion_page_id is required")

        # Generate job ID and create initial status
        job_id = str(uuid.uuid4())
        manual_service.active_jobs[job_id] = PublishStatus(
            job_id=job_id,
            status=JobState.STARTED,
            message="Starting publication process",
            progress=0.0,
        )

        # Add the publication process to background tasks
        background_tasks.add_task(
            manual_service.publish_manual,
            request.notion_page_id,
            request.selected_solution,
            request.target_languages,
            user_id,
        )

        return {"job_id": job_id}
    except ValueError as e:
        logger.error(f"Validation error in publish request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting publication: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}", response_model=Optional[PublishStatus])
async def get_job_status(
    job_id: str = FastAPIPath(..., description="The ID of the job to check"),
):
    """Get current status of a publication job"""
    try:
        status = await manual_service.get_job_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watch/{job_id}")
async def watch_publication(
    job_id: str = FastAPIPath(..., description="The ID of the job to watch"),
):
    """Watch publication progress using Server-Sent Events"""
    try:
        # Check if job exists first
        status = await manual_service.get_job_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")

        async def event_generator():
            retry_count = 0
            max_retries = 3

            while True:
                try:
                    status = await manual_service.get_job_status(job_id)
                    if not status:
                        if retry_count >= max_retries:
                            raise HTTPException(status_code=404, detail="Job not found")
                        retry_count += 1
                        await asyncio.sleep(1)
                        continue

                    yield {"data": status.model_dump_json()}

                    if status.status in [
                        "completed",
                        "completed_with_errors",
                        "failed",
                    ]:
                        break

                    await asyncio.sleep(1)

                except Exception as e:
                    logger.error(f"Error in event stream: {str(e)}")
                    if retry_count >= max_retries:
                        raise
                    retry_count += 1
                    await asyncio.sleep(1)

        return EventSourceResponse(event_generator())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting up event stream: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs", response_model=List[PublishStatus])
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(10, ge=1, le=100, description="Number of jobs to return"),
):
    """List recent publication jobs with optional status filter"""
    try:
        jobs = list(manual_service.active_jobs.values())

        if status:
            jobs = [job for job in jobs if job.status == status]

        # Sort by most recent first (assuming job_id contains timestamp)
        jobs.sort(key=lambda x: x.job_id, reverse=True)

        return jobs[:limit]
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications", response_model=List[Notification])
async def get_notifications(
    limit: int = Query(
        50, ge=1, le=100, description="Number of notifications to return"
    ),
    include_read: bool = Query(
        False, description="Whether to include read notifications"
    ),
    manual_service: ManualService = Depends(get_manual_service),
    current_user: TokenData = Depends(get_current_token_data),
):
    """Get recent notifications for the current authenticated user."""
    try:
        return await manual_service.get_notifications(
            limit=limit, include_read=include_read, user_id=current_user.username
        )
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications/latest", response_model=Optional[Notification])
async def get_latest_notification(
    include_read: bool = Query(
        False, description="Whether to include read notifications"
    ),
    manual_service: ManualService = Depends(get_manual_service),
    current_user: TokenData = Depends(get_current_token_data),
):
    """Get the latest notification only for the current authenticated user.

    Note: For real-time updates, consider using the /notifications/stream endpoint instead.
    """
    try:
        return await manual_service.get_notifications(
            include_read=include_read, user_id=current_user.username, latest_only=True
        )
    except Exception as e:
        logger.error(f"Error getting latest notification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications/stream")
async def stream_notifications(
    include_read: bool = Query(
        False, description="Whether to include read notifications"
    ),
    manual_service: ManualService = Depends(get_manual_service),
    current_user: TokenData = Depends(get_current_token_data),
):
    """Stream notifications in real-time using Server-Sent Events (SSE).

    This endpoint uses SSE to push notifications to the client in real-time.
    Clients will receive new notifications as they are created without polling.
    """
    try:

        async def event_generator():
            notification_queue = asyncio.Queue()

            # Register this client's queue
            queue_id = await manual_service.register_notification_client(
                queue=notification_queue, user_id=current_user.username
            )

            try:
                # First send existing notifications
                latest = await manual_service.get_notifications(
                    include_read=include_read,
                    user_id=current_user.username,
                    latest_only=True,
                )

                if latest:
                    yield {"data": latest.model_dump_json()}

                # Then listen for new notifications
                while True:
                    notification = await notification_queue.get()
                    if notification is None:  # None is our signal to stop
                        break

                    # Check if this notification should be sent to this user
                    user_id = notification.user_id
                    if user_id is None or user_id == current_user.username:
                        # Only send if we include read or it's unread
                        if include_read or not notification.is_read:
                            yield {"data": notification.model_dump_json()}

                    notification_queue.task_done()
            finally:
                # Always unregister the client when done
                await manual_service.unregister_notification_client(queue_id)

        return EventSourceResponse(event_generator())
    except Exception as e:
        logger.error(f"Error setting up notification stream: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str = FastAPIPath(
        ..., description="The ID of the notification to mark as read"
    ),
    manual_service: ManualService = Depends(get_manual_service),
):
    """Mark a notification as read."""
    try:
        success = await manual_service.mark_notification_read(notification_id)
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notifications/clear")
async def clear_notifications(
    manual_service: ManualService = Depends(get_manual_service),
):
    """Clear all notifications."""
    try:
        await manual_service.clear_notifications()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error clearing notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sidebar", response_model=SidebarMenu)
async def get_sidebar_menu(
    manual_service: ManualService = Depends(get_manual_service),
):
    """Get information about all available solutions for the sidebar menu."""
    try:
        solutions = []
        for solution_type in SolutionType:
            root_page_id = manual_service.root_page_ids.get(solution_type)
            if root_page_id:
                solutions.append(
                    SidebarMenuItem(
                        name=solution_type.value.upper(),
                        solution_type=solution_type,
                        root_page_id=root_page_id,
                    )
                )

        return SidebarMenu(solutions=solutions)
    except Exception as e:
        logger.error(f"Error getting sidebar menu: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
