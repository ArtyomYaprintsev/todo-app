import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Annotated
from fastapi import FastAPI, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, Session, Field, create_engine, select

from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlmodel import paginate


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


class HTTPError(SQLModel):
    detail: str


base_dir = Path(__file__).resolve().parent
sqlite_filename = os.getenv('SQLITE_DATABASE', 'db.sqlite3')

engine = create_engine(
    'sqlite:///%s' % (base_dir.parent / sqlite_filename),
    echo=True,
)

SQLModel.metadata.create_all(engine)


app = FastAPI()
add_pagination(app)


def select_task(task_id: int, session: Session):
    return session.exec(select(Task).where(Task.id == task_id)).first()


def save_task(task: Task, session: Session) -> Task:
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def get_session():
    with Session(engine) as session:
        yield session


def retrieve_task(
    task_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> Task:
    task = select_task(task_id, session)

    if task:
        return task

    raise HTTPException(
        status_code=404,
        detail='Task with the given [%d] id does not exist.' % task_id,
    )


@app.get('/tasks/', response_model=Page[Task], tags=['tasks'])
def get_all_tasks(session: Annotated[Session, Depends(get_session)]):
    return paginate(session, select(Task).order_by(Task.created))


@app.post('/tasks/', response_model=Task, tags=['tasks'])
def create_task(
    task: TaskCreate,
    session: Annotated[Session, Depends(get_session)],
):
    created_task = save_task(Task(**task.model_dump()), session)

    return JSONResponse(
        content=jsonable_encoder(created_task),
        status_code=201,
        headers={
            'Location': '/tasks/%d/' % created_task.id,
            'Content-Type': 'application/json',
        },
    )


@app.get(
    '/tasks/{task_id}/',
    response_model=Optional[Task],
    responses={
        404: {
            'model': HTTPError,
            'description': 'Task does not exist',
        },
    },
    tags=['tasks'],
)
def retrieve_task_instance(task: Annotated[int, Depends(retrieve_task)]):
    return task


@app.put(
    '/tasks/{task_id}/',
    response_model=Task,
    responses={
        404: {
            'model': HTTPError,
            'description': 'Task does not exist',
        },
    },
    tags=['tasks'],
)
def update_task_instance(
    task_update: TaskUpdate,
    task: Annotated[Task, Depends(retrieve_task)],
    session: Annotated[Session, Depends(get_session)],
):
    for field, value in task_update.model_dump().items():
        if value is not None:
            setattr(task, field, value)

    task.modified = datetime.now()
    return save_task(task, session)


@app.delete(
    '/tasks/{task_id}/',
    responses={
        204: {
            'model': None,
            'description': 'No content',
        },
        404: {
            'model': HTTPError,
            'description': 'Task does not exist',
        },
    },
    status_code=204,
    tags=['tasks'],
)
def delete_task_instance(
    task: Annotated[Task, Depends(retrieve_task)],
    session: Annotated[Session, Depends(get_session)],
):
    session.delete(task)
    session.commit()

    return JSONResponse(
        content=None,
        status_code=204,
        headers={"Cache-Control": "no-cache, no-store"},
    )
