from fastapi import FastAPI
from fastapi_pagination import add_pagination

from server.routers import tasks


app = FastAPI()

add_pagination(app)
app.include_router(tasks.router)
