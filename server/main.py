from fastapi import FastAPI
from fastapi_pagination import add_pagination

from server.routers import tasklists, tasks

app = FastAPI()

add_pagination(app)

app.include_router(tasklists.router)
app.include_router(tasks.router)
