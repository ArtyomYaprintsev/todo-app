from datetime import datetime

from sqlmodel import Field, SQLModel


class CreatedAtModel(SQLModel):
    """Model with `created_at` datetime field."""
    created_at: datetime = Field(default=datetime.now())


class ModifiedAtModel(SQLModel):
    """Model with `modified_at` datetime field."""
    modified_at: datetime = Field(default=datetime.now())


class TimestampModel(CreatedAtModel, ModifiedAtModel):
    """Combined with `CreatedAtModel` and `ModifiedAtModel`."""
