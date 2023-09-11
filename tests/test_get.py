import pytest

from app.message import Message


@pytest.fixture
def path():
    return "/GetMessage"


@pytest.mark.parametrize("query", [
    {"applicationId": 1},
    {"sessionId": "s1"},
    {"messageId": "m1"}
])
def test_get_message_non_existent(client, path, query):
    response = client.get(path, query_string=query)
    assert response.status_code == 404


@pytest.mark.parametrize("query", [
    None,
    {},
    {"key": "val"},
    {"applicationId": "str"}
])
def test_get_message_invalid_param(client, path, query):
    response = client.get(path, query_string=query)
    assert response.status_code == 400


@pytest.fixture
def message():
    return {
        "application_id": 1,
        "session_id": "s1",
        "message_id": "m1",
        "participants": ["john", "jack"],
        "content": "Hello, world!"
    }


@pytest.fixture
def message_object(data_store, message):
    message_object = Message(**message)
    data_store.add_message(message_object)

    return message_object


@pytest.fixture
def application_id(message_object):
    return message_object.application_id


@pytest.fixture
def session_id(message_object):
    return message_object.session_id


@pytest.fixture
def message_id(message_object):
    return message_object.message_id


def test_get_message_by_application_id(client, path, application_id, message):
    response = client.get(path, query_string={"applicationId": application_id})
    assert response.status_code == 200, f"Description: {response.json.get('description')}"
    assert response.json.get("messages")[0] == message


def test_get_message_session_id(client, path, session_id, message):
    response = client.get(path, query_string={"sessionId": session_id})
    assert response.status_code == 200, f"Description: {response.json.get('description')}"
    assert response.json.get("messages")[0] == message


def test_get_message_message_id(client, path, message_id, message):
    response = client.get(path, query_string={"messageId": message_id})
    assert response.status_code == 200, f"Description: {response.json.get('description')}"
    assert response.json.get("messages")[0] == message
