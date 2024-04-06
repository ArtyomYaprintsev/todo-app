from sqlmodel import SQLModel


class HTTPError(SQLModel):
    """Model for `HTTPException` raises."""
    detail: str
