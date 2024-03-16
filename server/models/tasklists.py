from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

from .datetimes import TimestampModel
from .tasks import Task


class TaskListBase(SQLModel):
    name: str = Field(max_length=150)


class TaskListCreate(TaskListBase):
    pass


class TaskListUpdate(SQLModel):
    name: Optional[str]


class TaskList(TaskListBase, TimestampModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    tasks: List[Task] = Relationship(back_populates="tasklist")
