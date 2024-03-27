from datetime import datetime
from typing import Any, Optional

import pytest
from fastapi.testclient import TestClient
from fastapi_pagination import Page, add_pagination
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from server.dependencies import get_session
from server.main import app
from server.models.tasklists import TaskList
from server.models.tasks import Task, TaskRead


@pytest.fixture(name='tasklist')
def tasklist_instance(session: Session):
    tasklist = TaskList(name='Test tasklist')
    session.add(tasklist)
    session.commit()
    session.refresh(tasklist)
    return tasklist


@pytest.fixture(name='task')
def task_instance(session: Session, tasklist: TaskList):
    task = Task(text='Test task', tasklist_id=tasklist.id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def test_get_tasks_list_deprecated(client: TestClient):
    response = client.get("/tasks/")
    assert response.status_code == 405


def test_create_task(client: TestClient, tasklist: TaskList):
    created_task_text = 'New test task'
    response = client.post(
        "/tasks/",
        json={
            'text': created_task_text,
            'tasklist_id': tasklist.id,
        },
    )
    assert response.status_code == 201

    response_task = Task(**response.json())

    # Verify that the response body matches the Task model
    assert isinstance(response_task, Task)
    assert response_task.text == created_task_text


@pytest.mark.parametrize(
    'invalid_data',
    [
        pytest.param({}, id='name_is_empty'),
        pytest.param({'name': "a" * 151}, id='name_too_long'),
    ],
)
def test_create_task_with_invalid_text(
    client: TestClient,
    tasklist: TaskList,
    invalid_data: dict[str, Any],
):
    response = client.post(
        '/tasks/',
        json={
            **invalid_data,
            'tasklist_id': tasklist.id,
        },
    )
    assert response.status_code == 422


def test_create_task_without_tasklist_id(client: TestClient):
    response = client.post('/tasks/', json={'text': 'Test task'})
    assert response.status_code == 422


def test_return_location_header_when_creating_task(
    client: TestClient,
    tasklist: TaskList,
):
    response = client.post(
        '/tasks/',
        json={
            'text': 'Task text',
            'tasklist_id': tasklist.id,
        },
    )
    assert response.status_code == 201

    created_task = TaskRead(**response.json())

    # Verify the response contains the Location header
    location: Optional[str] = response.headers.get('Location')
    assert location is not None

    location_response = client.get(location)
    retrieved_task = TaskRead(**location_response.json())

    assert (
        created_task.model_dump()
        == retrieved_task.model_dump()
    ), (
        'The created instance and retrieved by the following URL from the '
        '`Location` header do not match.'
    )


@pytest.mark.parametrize('http_method', ['GET', 'PUT', 'DELETE'])
def test_inexistent_task_returns_404(client: TestClient, http_method: str):
    inexistent_task_id = '1234567890'

    url = f'/tasklists/{inexistent_task_id}/'

    if http_method == 'PUT':
        response = client.put(url, json={})
    elif http_method == 'DELETE':
        response = client.delete(url)
    else:
        response = client.get(url)

    assert response.status_code == 404

    data = response.json()

    assert data.get('detail') not in ('', None), (
        'The `detail` field should not be empty.'
    )


def test_retrieve_task_instance(client: TestClient, task: Task):
    response = client.get('/tasks/%d/' % task.id)
    assert response.status_code == 200

    response_task = Task(**response.json())

    assert isinstance(response_task, Task)
    assert response_task.id == task.id
    assert response_task.text == task.text


def test_update_task_instance(client: TestClient, task: Task):
    updated_task_text = 'Updated task'
    updated_task_is_completed = not task.is_completed
    # Need to copy the given task data into the new variable, because
    # the `task` argument updates on client.put call
    #
    # To reproduce it, remove `initial_task` variable usage and replace it
    # with `task` argument instead
    initial_task = Task(**task.model_dump())

    if updated_task_text == task.text:
        raise ValueError(
            'Updated task text can not be equal with existed task text.',
        )

    response = client.put(
        f'/tasks/{task.id}/',
        json={
            'text': updated_task_text,
            'is_completed': updated_task_is_completed,
        },
    )

    assert response.status_code == 200

    response_task = TaskRead(**response.json())

    assert isinstance(response_task, TaskRead)
    assert response_task.id == initial_task.id

    # Verify that task has been updated
    assert response_task.text == updated_task_text
    assert response_task.is_completed == updated_task_is_completed

    # Verify that task created datetime is not changed
    assert response_task.created_at == initial_task.created_at

    # Verify that task modified datetime is changed
    assert response_task.modified_at > initial_task.modified_at


@pytest.mark.parametrize(
    'invalid_data',
    [pytest.param({'name': "a" * 151}, id='name_too_long')],
)
def test_update_task_instance_with_invalid_data(
    client: TestClient,
    task: Task,
    invalid_data: dict[str, Any]
):
    initial_task = TaskRead(**task.model_dump())

    response = client.put(f'/tasks/{task.id}/', json=invalid_data)
    assert response.status_code == 422, (
        'The task was updated with invalid data.'
    )

    retrieve_response = client.get(f'/tasks/{task.id}/')
    retrieved_task = TaskRead(**retrieve_response.json())

    assert initial_task.model_dump() == retrieved_task.model_dump(), (
        'The task was updated with invalid data.'
    )


def test_delete_task_instance(client: TestClient, task: Task):
    response = client.delete(f'/tasks/{task.id}/')
    assert response.status_code == 204
    assert response.headers.get('Cache-Control') == 'no-cache, no-store', (
        'The `cache-control` header was not set.'
    )

    retrieve_response = client.get(f'/tasks/{task.id}/')
    assert retrieve_response.status_code == 404, (
        'The tasklist was not deleted.'
    )
