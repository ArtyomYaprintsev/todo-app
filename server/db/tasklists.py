from datetime import datetime
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from server.dependencies import get_session
from server.models import TaskList


def get_tasklist(
    tasklist_id: int,
    session: Annotated[Session, Depends(get_session)],
):
    return session.exec(
        select(TaskList).where(TaskList.id == tasklist_id),
    ).first()


def save_tasklist(
    tasklist: TaskList,
    session: Annotated[Session, Depends(get_session)],
):
    tasklist.modified_at = datetime.now()

    session.add(tasklist)
    session.commit()
    session.refresh(tasklist)

    return tasklist


def retrieve_tasklist(
    tasklist_id: int,
    session: Annotated[Session, Depends(get_session)],
):
    tasklist = get_tasklist(tasklist_id, session)

    if tasklist:
        return tasklist

    raise HTTPException(
        status_code=404,
        detail=(
            'Task List with the given [%d] id does not exist.' % tasklist_id
        ),
    )
