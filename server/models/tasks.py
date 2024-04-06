from typing import Optional

from sqlmodel import Field, SQLModel

from .datetimes import TimestampModel


class TaskBase(SQLModel):
    """Base task model with `text` string field."""
    text: str = Field(max_length=150)


class TaskCreate(TaskBase):
    """Base task model for endpoint typing."""


class TaskUpdate(SQLModel):
    """Task model with changeable fields."""
    text: Optional[str]
    is_completed: Optional[bool]


class Task(TaskBase, TimestampModel, table=True):
    """Task model with table flag."""
    id: int = Field(default=None, primary_key=True)
    is_completed: bool = Field(default=False)
