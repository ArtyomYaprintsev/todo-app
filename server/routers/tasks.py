from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from server.db.tasks import retrieve_task, save_task
from server.dependencies import get_session
from server.models.errors import HTTPError
from server.models.tasks import Task, TaskCreate, TaskUpdate

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Depends(get_session)],
)


@router.get("/")
def get_all_tasks(
    session: Annotated[Session, Depends(get_session)],
) -> Page[Task]:
    """Get all tasks list."""
    return paginate(
        session,
        select(Task).order_by(Task.created_at),  # type: ignore[arg-type]
    )


@router.post("/", response_model=Task)
def create_task(
    task: TaskCreate,
    session: Annotated[Session, Depends(get_session)],
):
    """Create new task instance."""
    created_task = save_task(Task(**task.model_dump()), session)

    return JSONResponse(
        content=jsonable_encoder(created_task),
        status_code=201,
        headers={
            "Location": f"router.prefix/{created_task.id}/",
            "Content-Type": "application/json",
        },
    )


@router.get(
    "/{task_id}/",
    response_model=Optional[Task],
    responses={
        404: {
            "model": HTTPError,
            "description": "Task does not exist",
        },
    },
)
def retrieve_task_instance(task: Annotated[int, Depends(retrieve_task)]):
    """Retrieve task instance by id."""
    return task


@router.put(
    "/{task_id}/",
    response_model=Task,
    responses={
        404: {
            "model": HTTPError,
            "description": "Task does not exist",
        },
    },
)
def update_task_instance(
    task_update: TaskUpdate,
    task: Annotated[Task, Depends(retrieve_task)],
    session: Annotated[Session, Depends(get_session)],
):
    """Update task instance by id."""
    for field, value in task_update.model_dump().items():
        if value is not None:
            setattr(task, field, value)

    task.modified_at = datetime.now()
    return save_task(task, session)


@router.delete(
    "/{task_id}/",
    responses={
        204: {
            "model": None,
            "description": "No content",
        },
        404: {
            "model": HTTPError,
            "description": "Task does not exist",
        },
    },
    status_code=204,
)
def delete_task_instance(
    task: Annotated[Task, Depends(retrieve_task)],
    session: Annotated[Session, Depends(get_session)],
):
    """Delete task instance by id."""
    session.delete(task)
    session.commit()

    return JSONResponse(
        content=None,
        status_code=204,
        headers={"Cache-Control": "no-cache, no-store"},
    )
