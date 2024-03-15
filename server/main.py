from fastapi import FastAPI
from fastapi_pagination import add_pagination
from sqlmodel import SQLModel

from server.routers import tasks
from server.settings import ENGINE

SQLModel.metadata.create_all(ENGINE)

app = FastAPI()

add_pagination(app)
app.include_router(tasks.router)
