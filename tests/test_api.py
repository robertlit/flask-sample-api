import pytest

from app.api import app

add_message_path = "/AddMessage"
get_message_path = "/GetMessage"
delete_message_path = "/DeleteMessage"


@pytest.fixture
def client():
    return app.test_client()


def test_get_message_empty(client):
    response = client.get(get_message_path, query_string={"applicationId": 1})
    assert response.status_code == 404

    response = client.get(get_message_path, query_string={"sessionId": "s1"})
    assert response.status_code == 404

    response = client.get(get_message_path, query_string={"messageId": "m1"})
    assert response.status_code == 404


def test_delete_message_empty(client):
    response = client.get(delete_message_path, query_string={"applicationId": 1})
    assert response.status_code == 404

    response = client.get(delete_message_path, query_string={"sessionId": "s1"})
    assert response.status_code == 404

    response = client.get(delete_message_path, query_string={"messageId": "m1"})
    assert response.status_code == 404


def test_add_invalid_message(client):
    # No JSON body
    response = client.post(add_message_path)
    assert response.status_code == 400

    # Empty JSON
    response = client.post(add_message_path, json={})
    assert response.status_code == 400

    # Missing application_id
    response = client.post(add_message_path, json={
        "session_id": "aaa",
        "message_id": "bbb",
        "participants": ["john", "jack"],
        "content": "Hello, world!"
    })
    assert response.status_code == 400

    # Missing session_id
    response = client.post(add_message_path, json={
        "application_id": 1,
        "message_id": "bbb",
        "participants": ["john", "jack"],
        "content": "Hello, world!"
    })
    assert response.status_code == 400

    # Missing message_id
    response = client.post(add_message_path, json={
        "application_id": 1,
        "session_id": "aaa",
        "participants": ["john", "jack"],
        "content": "Hello, world!"
    })
    assert response.status_code == 400

    # Missing participants
    response = client.post(add_message_path, json={
        "application_id": 1,
        "session_id": "aaa",
        "message_id": "bbb",
        "content": "Hello, world!"
    })
    assert response.status_code == 400

    # Missing content
    response = client.post(add_message_path, json={
        "application_id": 1,
        "session_id": "aaa",
        "message_id": "bbb",
        "participants": ["john", "jack"],
    })
    assert response.status_code == 400

    # application_id is not int
    response = client.post(add_message_path, json={
        "application_id": "str",
        "session_id": "aaa",
        "message_id": "bbb",
        "participants": ["john", "jack"],
        "content": "Hello, world!"
    })
    assert response.status_code == 400

    # participants isn't a list
    response = client.post(add_message_path, json={
        "application_id": 1,
        "session_id": "aaa",
        "message_id": "bbb",
        "participants": "invalid",
        "content": "Hello, world!"
    })
    assert response.status_code == 400


def test_add_message(client):
    messages = [
        {
            "application_id": 1,
            "session_id": "s1",
            "message_id": "m1",
            "participants": ["john", "jack"],
            "content": "Hello, world!"
        },
        {
            "application_id": 1,
            "session_id": "s1",
            "message_id": "m2",
            "participants": ["john", "jack"],
            "content": "Hello, world!"
        },
        {
            "application_id": 1,
            "session_id": "s2",
            "message_id": "m3",
            "participants": ["john", "jack"],
            "content": "Hello, world!"
        },
        {
            "application_id": 2,
            "session_id": "s2",
            "message_id": "m4",
            "participants": ["john", "jack"],
            "content": "Hello, world!"
        },
        {
            "application_id": 2,
            "session_id": "s3",
            "message_id": "m5",
            "participants": ["john", "jack"],
            "content": "Hello, world!"
        }
    ]

    for message in messages:
        response = client.post(add_message_path, json=message)
        assert response.status_code == 200


def test_add_duplicate_message(client):
    response = client.post(add_message_path, json={
        "application_id": 1,
        "session_id": "s1",
        "message_id": "m1",
        "participants": ["john", "jack"],
        "content": "Hello, world!"
    })
    assert response.status_code == 400


def test_get_message_invalid(client):
    # No query parameters
    response = client.get(get_message_path)
    assert response.status_code == 400

    # Invalid query parameter
    response = client.get(get_message_path, query_string={"key": "val"})
    assert response.status_code == 400

    # application_id not int
    response = client.get(get_message_path, query_string={"applicationId": "str"})
    assert response.status_code == 400


required_fields = [("application_id", int),
                   ("session_id", str),
                   ("message_id", str),
                   ("participants", list),
                   ("content", str)]


def test_get_message_by_application_id(client):
    response = client.get(get_message_path, query_string={"applicationId": 1})
    assert response.status_code == 200
    assert len(response.json["messages"]) == 3
    for message in response.json["messages"]:
        assert message["application_id"] == 1
        for field_name, field_type in required_fields:
            assert field_name in message
            assert isinstance(message[field_name], field_type)


def test_get_message_by_session_id(client):
    response = client.get(get_message_path, query_string={"sessionId": "s1"})
    assert response.status_code == 200
    assert len(response.json["messages"]) == 2
    for message in response.json["messages"]:
        assert message["session_id"] == "s1"
        for field_name, field_type in required_fields:
            assert field_name in message
            assert isinstance(message[field_name], field_type)


def test_get_message_by_message_id(client):
    response = client.get(get_message_path, query_string={"messageId": "m1"})
    assert response.status_code == 200
    assert len(response.json["messages"]) == 1
    for message in response.json["messages"]:
        assert message["message_id"] == "m1"
        for field_name, field_type in required_fields:
            assert field_name in message
            assert isinstance(message[field_name], field_type)


def test_delete_message_invalid(client):
    # No query parameters
    response = client.get(delete_message_path)
    assert response.status_code == 400

    # Invalid query parameter
    response = client.get(delete_message_path, query_string={"key": "val"})
    assert response.status_code == 400

    # application_id not int
    response = client.get(delete_message_path, query_string={"applicationId": "str"})
    assert response.status_code == 400


def test_delete_message_by_application_id(client):
    response = client.get(delete_message_path, query_string={"applicationId": 1})
    assert response.status_code == 200
    assert response.json["deleted_amount"] == 3


def test_delete_message_by_session_id(client):
    response = client.get(delete_message_path, query_string={"sessionId": "s2"})
    assert response.status_code == 200
    assert response.json["deleted_amount"] == 1


def test_delete_message_by_message_id(client):
    response = client.get(delete_message_path, query_string={"messageId": "m5"})
    assert response.status_code == 200
    assert response.json["deleted_amount"] == 1
