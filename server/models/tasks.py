from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from .datetimes import TimestampModel


if TYPE_CHECKING:
    from .tasklists import TaskList


class TaskBase(SQLModel):
    text: str = Field(max_length=150)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    text: Optional[str]
    is_completed: Optional[bool]


class Task(TaskBase, TimestampModel, table=True):
    id: int = Field(default=None, primary_key=True)
    is_completed: bool = Field(default=False)

    tasklist_id: int = Field(foreign_key="tasklist.id")
    tasklist: Optional["TaskList"] = Relationship(back_populates="tasks")
