from datetime import datetime

from sqlmodel import Field, SQLModel


class CreatedAdModel(SQLModel):
    created_at: datetime = Field(default=datetime.now())


class ModifiedAtModel(SQLModel):
    modified_at: datetime = Field(default=datetime.now())


class TimestampModel(CreatedAdModel, ModifiedAtModel):
    pass
