from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from server.db.tasklists import retrieve_tasklist, save_tasklist
from server.dependencies import get_session
from server.models.tasklists import (TaskList, TaskListCreate, TaskListRead,
                                     TaskListUpdate, TaskListWithTasks)

router = APIRouter(prefix='/tasklists', tags=['tasklists'])


@router.get('/', response_model=Page[TaskListRead])
def get_tasklists(session: Annotated[Session, Depends(get_session)]):
    return paginate(session, select(TaskList).order_by(TaskList.created_at))


@router.post('/', response_model=TaskListRead)
def create_tasklist(
    tasklist: TaskListCreate,
    session: Annotated[Session, Depends(get_session)],
):
    created_tasklist = save_tasklist(
        TaskList(**tasklist.model_dump()), session)

    return JSONResponse(
        content=jsonable_encoder(created_tasklist),
        status_code=201,
        headers={
            'Location': router.prefix + '/%d/' % created_tasklist.id,
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache, no-store',
        },
    )


@router.get('/{tasklist_id}/', response_model=Optional[TaskListWithTasks])
def retrieve_tasklist_instance(
    tasklist: Annotated[TaskListRead, Depends(retrieve_tasklist)],
):
    return tasklist


@router.put('/{tasklist_id}/', response_model=Optional[TaskListRead])
def update_tasklist_instance(
    tasklist_update: TaskListUpdate,
    tasklist: Annotated[TaskListRead, Depends(retrieve_tasklist)],
    session: Annotated[Session, Depends(get_session)],
):
    for field, value in tasklist_update.model_dump().items():
        if value is not None:
            setattr(tasklist, field, value)

    return save_tasklist(tasklist, session)


@router.delete('/{tasklist_id}/')
def delete_tasklist_instance(
    tasklist: Annotated[TaskListRead, Depends(retrieve_tasklist)],
    session: Annotated[Session, Depends(get_session)],
):
    session.delete(tasklist)
    session.commit()

    return JSONResponse(
        content=None,
        status_code=204,
        headers={"Cache-Control": "no-cache, no-store"},
    )
