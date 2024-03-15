from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TaskBase(SQLModel):
    text: str


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    text: Optional[str]
    is_completed: Optional[bool]


class Task(TaskBase, table=True):
    id: int = Field(default=None, primary_key=True)
    text: str = Field(max_length=150)
    is_completed: bool = Field(default=False)

    modified: datetime = Field(default=datetime.now())
    created: datetime = Field(default=datetime.now())
