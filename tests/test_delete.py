import pytest

from app.message import Message


@pytest.fixture
def path():
    return "/DeleteMessage"


@pytest.mark.parametrize("query", [
    {"applicationId": 1},
    {"sessionId": "s1"},
    {"messageId": "m1"}
])
def test_get_delete_non_existent(client, path, query):
    response = client.delete(path, query_string=query)
    assert response.status_code == 404


@pytest.mark.parametrize("query", [
    None,
    {},
    {"key": "val"},
    {"applicationId": "str"}
])
def test_delete_message_invalid_param(client, path, query):
    response = client.delete(path, query_string=query)
    assert response.status_code == 400


@pytest.fixture
def message(data_store):
    message = {
        "application_id": 1,
        "session_id": "s1",
        "message_id": "m1",
        "participants": ["john", "jack"],
        "content": "Hello, world!"
    }

    message_object = Message(**message)
    data_store.add_message(message_object)

    return message_object


@pytest.fixture
def application_id(message):
    return message.application_id


@pytest.fixture
def session_id(message):
    return message.session_id


@pytest.fixture
def message_id(message):
    return message.message_id


def test_delete_message_by_application_id(client, path, application_id):
    response = client.delete(path, query_string={"applicationId": application_id})
    assert response.status_code == 200, f"Description: {response.json.get('description')}"
    assert response.json["deleted_amount"] == 1


def test_delete_message_by_session_id(client, path, session_id):
    response = client.delete(path, query_string={"sessionId": session_id})
    assert response.status_code == 200, f"Description: {response.json.get('description')}"
    assert response.json["deleted_amount"] == 1


def test_delete_message_by_message_id(client, path, message_id):
    response = client.delete(path, query_string={"messageId": message_id})
    assert response.status_code == 200, f"Description: {response.json.get('description')}"
    assert response.json["deleted_amount"] == 1
