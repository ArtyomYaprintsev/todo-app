from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from .datetimes import TimestampModel
from .tasks import Task, TaskRead


class TaskListName(SQLModel):
    """Model representing a task list name."""
    name: str = Field(max_length=150)


class TaskListRead(TaskListName, TimestampModel):
    """Read-only model for task lists."""
    id: int


class TaskList(TaskListRead, table=True):
    """The `TaskList` model with db table relation."""
    id: Optional[int] = Field(default=None, primary_key=True)

    tasks: List[Task] = Relationship(
        back_populates="tasklist",
        sa_relationship_kwargs={
            "cascade": "all,delete,delete-orphan",
        },
    )


class TaskListCreate(TaskListName):
    pass


class TaskListUpdate(SQLModel):
    name: Optional[str] = Field(max_length=150)


class TaskListWithTasks(TaskListRead):
    tasks: List[TaskRead] = []
