from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from fastapi_pagination import Page, add_pagination
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from server.dependencies import get_session
from server.main import app
from server.models.tasks import Task


@pytest.fixture(name="session")
def session_fixture():
    """Create session with sqlite database."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Init a test client with session."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(add_pagination(app))
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="task")
def task_instance(session: Session):
    """Create task instance."""
    task = Task(text="Test task")
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def test_read_tasks_list(client: TestClient):
    """Test all tasks read API endpoint."""
    response = client.get("/tasks/")
    assert response.status_code == 200

    # Verify that the response body matches the Page model
    page = Page(**response.json())
    assert isinstance(page, Page)

    # Verify that the page items matches the Task model
    for item in page.items:
        assert isinstance(Task(**item), Task)


def test_create_item(client: TestClient):
    """Test task creation API endpoint."""
    created_task_text = "New test task"
    response = client.post(
        "/tasks/",
        json={"text": created_task_text},
    )
    assert response.status_code == 201

    response_task = Task(**response.json())

    # Verify that the response body matches the Task model
    assert isinstance(response_task, Task)
    assert response_task.text == created_task_text

    # Verify the response contains the Location header
    assert response.headers.get("Location") == "/tasks/%d/" % response_task.id


def test_create_item_without_text(client: TestClient):
    """Test invalid task creation API endpoint."""
    response = client.post("/tasks/", json={})
    assert response.status_code == 422


@pytest.mark.parametrize("http_method", ["GET", "PUT", "DELETE"])
def test_inexistent_task_returns_404(client: TestClient, http_method: str):
    """Test inexistent task instance retrieve API endpoint."""
    inexistent_task_id = 999
    url = f"/tasks/{inexistent_task_id}/"
    expected_detail = (
        f"Task with the given [{inexistent_task_id}] id does not exist."
    )

    if http_method == "PUT":
        response = client.put(url, json={})
    elif http_method == "DELETE":
        response = client.delete(url)
    else:
        response = client.get(url)

    assert response.status_code == 404

    data = response.json()
    assert data == {"detail": expected_detail}


def test_retrieve_task_instance(client: TestClient, task: Task):
    """Test task instance retrieve API endpoint."""
    response = client.get("/tasks/%d/" % task.id)
    assert response.status_code == 200

    response_task = Task(**response.json())
    assert isinstance(response_task, Task)
    assert response_task.id == task.id
    assert response_task.text == task.text


def test_update_task_instance(client: TestClient, task: Task):
    """Test task instance update API endpoint."""
    updated_task_text = "Update task text"
    updated_task_is_completed = not task.is_completed
    # Need to copy the given task data into the new variable, because
    # the `task` argument updates on client.put call
    #
    # To reproduce it, remove `initial_task` variable usage and replace it
    # with `task` argument instead
    initial_task = Task(**task.model_dump())

    if updated_task_text == task.text:
        raise ValueError(
            "Updated task text can not be equal with existed task text.",
        )

    response = client.put(
        f"/tasks/{task.id}/",
        json={
            "text": updated_task_text,
            "is_completed": updated_task_is_completed,
        },
    )

    assert response.status_code == 200

    response_task = Task(**response.json())
    response_task.modified_at = datetime.fromisoformat(
        response_task.modified_at,
    )
    response_task.created_at = datetime.fromisoformat(
        response_task.created_at,
    )

    assert isinstance(response_task, Task)
    assert response_task.id == initial_task.id

    # Verify that task has been updated
    assert response_task.text == updated_task_text
    assert response_task.is_completed == updated_task_is_completed

    # Verify that task modified datetime is changed
    assert response_task.modified_at > initial_task.modified_at
    # Verify that task created datetime is not changed
    assert response_task.created_at == initial_task.created_at


def test_update_task_instance_with_invalid_data(
    client: TestClient,
    task: Task,
):
    """Test invalid task instance update API endpoint."""
    invalid_task_text = "the_random_text_with_more_then_150_chars" * 10
    response = client.put(
        f"/tasks/{task.id}/",
        json={"text": invalid_task_text},
    )
    assert response.status_code == 422


def test_delete_task_instance(client: TestClient, task: Task):
    """Test task instance delete API endpoint."""
    response = client.delete(f"/tasks/{task.id}/")
    assert response.status_code == 204
    assert response.headers.get("Cache-Control") == "no-cache, no-store"

    retrieve_response = client.get(f"/tasks/{task.id}/")
    assert retrieve_response.status_code == 404
