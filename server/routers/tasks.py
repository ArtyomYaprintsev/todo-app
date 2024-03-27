from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import Session

from server.db.tasklists import retrieve_tasklist
from server.db.tasks import retrieve_task, save_task
from server.dependencies import get_session
from server.models.errors import HTTPError
from server.models.tasks import Task, TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post('/', response_model=TaskRead)
def create_task(
    task: TaskCreate,
    session: Annotated[Session, Depends(get_session)],
):
    # Check the related tasklists existence
    retrieve_tasklist(task.tasklist_id, session)

    created_task = save_task(Task(**task.model_dump()), session)

    return JSONResponse(
        content=jsonable_encoder(created_task),
        status_code=201,
        headers={
            'Location': router.prefix + '/%d/' % created_task.id,
            'Content-Type': 'application/json',
        },
    )


@router.get(
    '/{task_id}/',
    response_model=Optional[TaskRead],
    responses={
        404: {
            'model': HTTPError,
            'description': 'Task does not exist',
        },
    },
)
def retrieve_task_instance(task: Annotated[int, Depends(retrieve_task)]):
    return task


@router.put(
    '/{task_id}/',
    response_model=TaskRead,
    responses={
        404: {
            'model': HTTPError,
            'description': 'Task does not exist',
        },
    },
)
def update_task_instance(
    task_update: TaskUpdate,
    task: Annotated[Task, Depends(retrieve_task)],
    session: Annotated[Session, Depends(get_session)],
):
    for field, value in task_update.model_dump().items():
        if value is not None:
            setattr(task, field, value)

    task.modified_at = datetime.now()
    return save_task(task, session)


@router.delete(
    '/{task_id}/',
    responses={
        204: {
            'model': None,
            'description': 'No content',
        },
        404: {
            'model': HTTPError,
            'description': 'Task does not exist',
        },
    },
    status_code=204,
)
def delete_task_instance(
    task: Annotated[Task, Depends(retrieve_task)],
    session: Annotated[Session, Depends(get_session)],
):
    session.delete(task)
    session.commit()

    return JSONResponse(
        content=None,
        status_code=204,
        headers={"Cache-Control": "no-cache, no-store"},
    )
