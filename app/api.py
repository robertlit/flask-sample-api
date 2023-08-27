import json
from dataclasses import fields

from flask import Flask, request, abort
from werkzeug.exceptions import HTTPException

from app.data import DataStore, MemoryDataStore, DiskDataStore
from app.message import Message

app = Flask(__name__)

# Leave one of the two uncommented, depending on which you want to use
data_store: DataStore = MemoryDataStore()
# data_store: DataStore = DiskDataStore()

required_fields = [(field.name, field.type) for field in fields(Message)]


def validate_message_data(data) -> (bool, str):
    for field_name, field_type in required_fields:
        if field_name not in data:
            return False, f"Missing {field_name}"

        if not isinstance(data[field_name], field_type):
            return False, f"Invalid type for {field_name}: {field_type.__name__} expected"

    return True, None


@app.post("/AddMessage")
def add_message():
    data = request.get_json(force=True, silent=True)
    if data is None:
        abort(400, "Invalid request body: JSON expected")

    is_valid, error_message = validate_message_data(data)
    if not is_valid:
        abort(400, error_message)

    message = Message(**data)
    if data_store.get_message_by_message_id(message.message_id):
        abort(400, f"Message with message_id={message.message_id} already exists")

    data_store.add_message(message)
    return {
        "result": "Message added successfully"
    }


@app.get("/GetMessage")
def get_message():
    if len(request.args.keys()) != 1:
        abort(400, "Specify exactly one of the following: applicationId, sessionId, messageId")

    if "applicationId" in request.args:
        try:
            application_id = int(request.args.get("applicationId"))
        except ValueError:
            abort(400, "applicationId must be an integer")

        messages = data_store.get_messages_by_application_id(application_id)

    elif "sessionId" in request.args:
        session_id = request.args.get("sessionId")
        messages = data_store.get_messages_by_session_id(session_id)

    elif "messageId" in request.args:
        message_id = request.args.get("messageId")
        message = data_store.get_message_by_message_id(message_id)
        messages = [message] if message else []

    else:
        abort(400, "Specify one of the following: applicationId, sessionId, messageId")

    if len(messages) == 0:
        abort(404, "No messages found")

    # always return in the same format to avoid api inconsistency
    return {
        "messages": messages
    }


@app.route("/DeleteMessage", methods=["DELETE", "GET"])
def delete_message():
    if len(request.args.keys()) != 1:
        abort(400, "Specify exactly one of the following: applicationId, sessionId, messageId")

    if "applicationId" in request.args:
        try:
            application_id = int(request.args.get("applicationId"))
        except ValueError:
            abort(400, "applicationId must be an integer")

        deleted_amount = data_store.delete_messages_by_application_id(application_id)

    elif "sessionId" in request.args:
        session_id = request.args.get("sessionId")
        deleted_amount = data_store.delete_messages_by_session_id(session_id)

    elif "messageId" in request.args:
        message_id = request.args.get("messageId")
        deleted_amount = data_store.delete_message_by_message_id(message_id)

    else:
        abort(400, "Specify one of the following: applicationId, sessionId, messageId")

    if deleted_amount == 0:
        abort(404, "No messages found")

    return {
        "deleted_amount": deleted_amount
    }


@app.errorhandler(HTTPException)
def handle_exception(e: HTTPException):
    """Return JSON instead of HTML for HTTP errors."""
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description
    })
    response.content_type = "application/json"
    return response
