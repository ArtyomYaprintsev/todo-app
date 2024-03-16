from typing import Optional

from sqlmodel import Field, SQLModel

from .datetimes import TimestampModel


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
