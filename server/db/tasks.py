from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from server.dependencies import get_session
from server.models.tasks import Task


def select_task(task_id: int, session: Session):
    return session.exec(select(Task).where(Task.id == task_id)).first()


def save_task(task: Task, session: Session) -> Task:
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def retrieve_task(
    task_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> Task:
    task = select_task(task_id, session)

    if task:
        return task

    raise HTTPException(
        status_code=404,
        detail='Task with the given [%d] id does not exist.' % task_id,
    )
