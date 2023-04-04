import json
import requests
import uuid

from tests.support.assertions import assert_valid_schema

TEST_ENDPOINT = "http://todo.pixegami.io"


def test_call_endpoint():
    response = requests.get(TEST_ENDPOINT)
    assert response.status_code == 200

    json_data = json.loads(response.content)
    assert_valid_schema(json_data, 'call_endpoint.json')


def test_create_task():
    payload = new_task_payload()
    create_task_response = create_task(payload)
    assert create_task_response.status_code == 200
    data = create_task_response.json()

    json_data = json.loads(create_task_response.content)
    assert_valid_schema(json_data, 'create_task.json')

    task_id = data["task"]["task_id"]
    get_task_response = get_task(task_id)

    json_data = json.loads(create_task_response.content)
    assert_valid_schema(json_data, 'get_task.json')

    assert get_task_response.status_code == 200
    get_task_data = get_task_response.json()
    assert get_task_data["content"] == payload["content"]
    assert get_task_data["user_id"] == payload["user_id"]


def test_can_update_task():
    # create a task
    payload = new_task_payload()
    create_task_response = create_task(payload)
    assert create_task_response.status_code == 200
    task_id = create_task_response.json()["task"]["task_id"]

    json_data = json.loads(create_task_response.content)
    assert_valid_schema(json_data, 'get_task.json')

    # update the task
    new_payload = {
        "user_id": payload["user_id"],
        "task_id": task_id,
        "content": "Test content for testing ENDPOINT API",
        "is_done": True
    }
    update_task_response = update_task(new_payload)
    assert update_task_response.status_code == 200

    json_data = json.loads(create_task_response.content)
    assert_valid_schema(json_data, 'get_task.json')

    # get and validate the changes
    get_task_response = get_task(task_id)
    assert get_task_response.status_code == 200
    get_task_data = get_task_response.json()
    assert get_task_data["content"] == new_payload["content"]
    assert get_task_data["is_done"] == new_payload["is_done"]


def test_can_list_tasks():
    # create N tasks
    n = 3
    payload = new_task_payload()
    for _ in range(n):
        create_task_response = create_task(payload)
        assert create_task_response.status_code == 200

    # list tasks and check that there are N items
    user_id = payload["user_id"]
    list_tasks_response = list_tasks(user_id)
    assert list_tasks_response.status_code == 200
    data = list_tasks_response.json()

    # Check that amount of tasks is right
    tasks = data["tasks"]
    assert len(tasks) == n

    assert_valid_schema(tasks, 'get_tasks_list.json')


def test_can_delete_task():
    # Create a task
    payload = new_task_payload()
    create_task_response = create_task(payload)
    assert create_task_response.status_code == 200
    task_id = create_task_response.json()["task"]["task_id"]

    # Delete the task
    delete_task_response = delete_task(task_id)
    assert delete_task_response.status_code == 200

    json_data = json.loads(delete_task_response.content)
    assert_valid_schema(json_data, 'get_task.json')

    # Get the task, and check that it's not found
    get_task_response = get_task(task_id)
    assert get_task_response.status_code == 404


def create_task(payload):
    return requests.put(TEST_ENDPOINT + "/create-task", json=payload)


def update_task(payload):
    return requests.put(TEST_ENDPOINT + "/update-task", json=payload)


def get_task(task_id):
    return requests.get(TEST_ENDPOINT + f"/get-task/{task_id}")


def list_tasks(user_id):
    return requests.get(TEST_ENDPOINT + f"/list-tasks/{user_id}")


def delete_task(task_id):
    return requests.delete(TEST_ENDPOINT + f"/delete-task/{task_id}")


def new_task_payload():
    user_id = f"test_user_{uuid.uuid4().hex}"
    content = f"test_content_{uuid.uuid4().hex}"

    return {
        "user_id": user_id,
        "content": content,
        "is_done": False
    }
