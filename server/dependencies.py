from sqlmodel import Session

from server.settings import ENGINE


def get_session():
    with Session(ENGINE) as session:
        yield session
