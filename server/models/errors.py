from sqlmodel import SQLModel


class HTTPError(SQLModel):
    detail: str
