from typing import Any, Optional

import pytest
from fastapi.testclient import TestClient
from fastapi_pagination import Page
from sqlmodel import Session

from server.models.tasklists import TaskList, TaskListRead, TaskListWithTasks
from server.models.tasks import Task, TaskRead


@pytest.fixture(name='tasklist')
def tasklist_instance(session: Session):
    tasklist = TaskList(name='Test tasklist')
    session.add(tasklist)
    session.commit()
    session.refresh(tasklist)
    return tasklist


def test_read_tasklists_list(client: TestClient):
    response = client.get('/tasklists/')
    assert response.status_code == 200

    # Verify the response matches the Page model
    page = Page(**response.json())
    assert isinstance(page, Page)

    # Verify the each page item matches the TaskList model
    for item in page.items:
        assert isinstance(TaskList(**item), TaskList)


def test_create_tasklists(client: TestClient):
    name = 'Test tasklist'
    response = client.post('/tasklists/', json={'name': name})
    assert response.status_code == 201

    created_tasklist = TaskList(**response.json())

    # Verify the response matches the TaskList model
    assert isinstance(created_tasklist, TaskList), (
        'The response is not the TaskList model instance'
    )
    assert created_tasklist.name == name


@pytest.mark.parametrize(
    'invalid_data',
    [
        pytest.param({}, id='name_is_empty'),
        pytest.param({'name': "a" * 151}, id='name_too_long'),
    ],
)
def test_return_422_when_creation_invalid_tasklist(
    client: TestClient,
    invalid_data: dict[str, Any],
):
    response = client.post('/tasklists/', json=invalid_data)
    assert response.status_code == 422


def test_return_location_header_when_creating_tasklist(client: TestClient):
    name = 'Test tasklist'

    response = client.post('/tasklists/', json={'name': name})
    assert response.status_code == 201

    created_tasklist = TaskListRead(**response.json())

    # Verify the response contains the Location header
    location: Optional[str] = response.headers.get('Location')
    assert location is not None

    location_response = client.get(location)
    retrieved_tasklist = TaskListRead(**location_response.json())

    assert (
        created_tasklist.model_dump()
        == retrieved_tasklist.model_dump()
    ), (
        'The created instance and retrieved by the following URL from the '
        '`Location` header do not match.'
    )


@pytest.mark.parametrize('http_method', ['GET', 'PUT', 'DELETE'])
def test_inexistent_tasklist_returns_404(client: TestClient, http_method: str):
    inexistent_tasklist_id = '1234567890'

    url = f'/tasklists/{inexistent_tasklist_id}/'

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


@pytest.mark.parametrize(
    'tasks_count',
    [
        pytest.param(0, id='without_tasks'),
        pytest.param(5, id='with_5_tasks'),
    ]
)
def test_retrieve_tasklist_without_tasks(
    session: Session,
    client: TestClient,
    tasklist: TaskList,
    tasks_count: int,
):
    for index in range(tasks_count):
        session.add(Task(text=f'Task {index}', tasklist_id=tasklist.id))
    session.commit()

    response = client.get(f'/tasklists/{tasklist.id}/')

    retrieved_tasklist = TaskListRead(**response.json())
    retrieved_tasklist_with_tasks = TaskListWithTasks(**response.json())

    assert retrieved_tasklist.model_dump() == tasklist.model_dump(), (
        'The retrieved instance does not match.'
    )

    assert len(retrieved_tasklist_with_tasks.tasks) == tasks_count, (
        'The retrieved tasklist tasks count does not match with expected '
        f'value. Expected tasks count: {tasks_count}.'
    )

    for task in retrieved_tasklist_with_tasks.tasks:
        assert isinstance(task, TaskRead), (
            'The retrieved tasklist tasks are not instances of the TaskRead '
            'model.'
        )


def test_update_tasklist(client: TestClient, tasklist: TaskList):
    new_name = 'Updated tasklist'
    initial_tasklist = TaskListRead(**tasklist.model_dump())

    response = client.put(
        f'/tasklists/{tasklist.id}/',
        json={'name': new_name},
    )
    assert response.status_code == 200

    updated_tasklist = TaskListRead(**response.json())

    assert updated_tasklist.name == new_name, (
        'The tasklist name not updated.'
    )

    assert updated_tasklist.id == tasklist.id, ('The ID does not match.')

    assert updated_tasklist.created_at == initial_tasklist.created_at, (
        'The `created_at` field does not match.'
    )

    assert updated_tasklist.modified_at > initial_tasklist.modified_at, (
        'The `modified_at` field not updated.'
    )


@pytest.mark.parametrize(
    'invalid_data',
    [pytest.param({'name': "a" * 151}, id='name_too_long')],
)
def test_update_with_invalid_data(
    client: TestClient,
    tasklist: TaskList,
    invalid_data: dict[str, Any],
):
    initial_tasklist = TaskListRead(**tasklist.model_dump())

    update_response = client.put(
        f'/tasklists/{tasklist.id}/',
        json=invalid_data,
    )

    assert update_response.status_code == 422, (
        'The tasklist was updated with invalid data.'
    )

    retrieve_response = client.get(f'/tasklists/{tasklist.id}/')
    retrieved_tasklist = TaskListRead(**retrieve_response.json())

    assert initial_tasklist.model_dump() == retrieved_tasklist.model_dump(), (
        'The tasklist was updated with invalid data.'
    )


def test_delete_tasklist(client: TestClient, tasklist: TaskList):
    response = client.delete(f'/tasklists/{tasklist.id}/')
    assert response.status_code == 204
    assert response.headers.get('cache-control') == 'no-cache, no-store', (
        'The `cache-control` header should be set.'
    )

    retrieve_response = client.get(f'/tasklists/{tasklist.id}/')
    assert retrieve_response.status_code == 404, (
        'The tasklist was not deleted.'
    )
