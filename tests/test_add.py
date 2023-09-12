import pytest

from app.message import Message


@pytest.fixture
def path():
    return "/AddMessage"


def test_add_no_json_body(client, path):
    response = client.post(path)
    assert response.status_code == 400


@pytest.mark.parametrize("message, desc", [
    ({}, "Empty JSON object"),
    ([], "Not a JSON object"),
    ({
         "session_id": "aaa",
         "message_id": "bbb",
         "participants": ["john", "jack"],
         "content": "Hello, world!"
     }, "Missing application_id"),
    ({
         "application_id": 1,
         "message_id": "bbb",
         "participants": ["john", "jack"],
         "content": "Hello, world!"
     }, "Missing session_id"),
    ({
         "application_id": 1,
         "session_id": "aaa",
         "participants": ["john", "jack"],
         "content": "Hello, world!"
     }, "Missing message_id"),
    ({
         "application_id": 1,
         "session_id": "aaa",
         "message_id": "bbb",
         "content": "Hello, world!"
     }, "Missing participants"),
    ({
         "application_id": 1,
         "session_id": "aaa",
         "message_id": "bbb",
         "participants": ["john", "jack"],
     }, "Missing content"),
    ({
         "application_id": "str",
         "session_id": "aaa",
         "message_id": "bbb",
         "participants": ["john", "jack"],
         "content": "Hello, world!"
     }, "application_id not int"),
    ({
         "application_id": 1,
         "session_id": "aaa",
         "message_id": "bbb",
         "participants": "invalid",
         "content": "Hello, world!"
     }, "participants not list")
])
def test_add_missing_messages(client, path, message, desc):
    response = client.post(path, json=message)
    assert response.status_code == 400, desc


@pytest.mark.parametrize("message", [{
    "application_id": 1,
    "session_id": "s1",
    "message_id": "m1",
    "participants": ["john", "jack"],
    "content": "Hello, world!"
}])
def test_add_message(client, path, message):
    response = client.post(path, json=message)
    assert response.status_code == 200, f"Description: {response.json.get('description')}"


@pytest.fixture
def duplicate_message(data_store):
    message = {
        "application_id": 1,
        "session_id": "s1",
        "message_id": "m1",
        "participants": ["john", "jack"],
        "content": "Hello, world!"
    }
    message_obj = Message(**message)
    data_store.add_message(message_obj)

    return message


def test_add_duplicate_message(client, path, duplicate_message):
    response = client.post(path, json=duplicate_message)
    assert response.status_code == 400
