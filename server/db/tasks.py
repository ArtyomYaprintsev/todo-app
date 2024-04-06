from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from server.dependencies import get_session
from server.models.tasks import Task


def select_task(task_id: int, session: Session):
    """Select task instance by the id."""
    return session.exec(select(Task).where(Task.id == task_id)).first()


def save_task(task: Task, session: Session):
    """Save task instance."""
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def retrieve_task(
    task_id: int,
    session: Annotated[Session, Depends(get_session)],
):
    """Retrieve task instance.

    Raises:
        HTTPException: if task instance by the given id does not exist.
    """
    task = select_task(task_id, session)

    if task:
        return task

    raise HTTPException(
        status_code=404,
        detail=f"Task with the given [{task_id}] id does not exist.",
    )
