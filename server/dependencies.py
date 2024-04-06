from sqlmodel import Session

from server.settings import ENGINE


def get_session():
    """Return database session in content."""
    with Session(ENGINE) as session:
        yield session
