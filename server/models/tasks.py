from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from .datetimes import TimestampModel

if TYPE_CHECKING:
    from .tasklists import TaskList, TaskListRead


class TaskBase(SQLModel):
    text: str = Field(max_length=150)
    tasklist_id: int = Field(foreign_key="tasklist.id")


class TaskRead(TaskBase, TimestampModel):
    id: int
    is_completed: bool = Field(default=False)


class Task(TaskRead, table=True):
    id: int = Field(default=None, primary_key=True)

    tasklist: Optional["TaskList"] = Relationship(back_populates="tasks")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    text: Optional[str] = Field(max_length=150)
    is_completed: Optional[bool]


class TaskWithTaskList(TaskRead):
    tasklist: Optional["TaskListRead"] = None
