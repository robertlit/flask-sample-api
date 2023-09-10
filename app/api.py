import json
from dataclasses import fields
from typing import Callable, Dict, Tuple, Any, List

from flask import Flask, request, abort
from werkzeug.exceptions import HTTPException

from app.data import DataStore, MemoryDataStore, DiskDataStore
from app.message import Message
from app.parsing import parse_int, identity
from app.validation import validate_message_data

app = Flask(__name__)

# Leave one of the two uncommented, depending on which you want to use
# data_store: DataStore = MemoryDataStore()
data_store: DataStore = DiskDataStore()

arg_transformations: Dict[str, Tuple[Callable[[str], Any], str]] = {
    "applicationId": (parse_int, "applicationId must be an integer"),
    "sessionId": (identity, None),
    "messageId": (identity, None)
}

get_functions: Dict[str, Callable[[Any], List[Message]]] = {
    "applicationId": data_store.get_messages_by_application_id,
    "sessionId": data_store.get_messages_by_session_id,
    "messageId": data_store.get_message_by_message_id
}

delete_functions: Dict[str, Callable[[Any], int]] = {
    "applicationId": data_store.delete_messages_by_application_id,
    "sessionId": data_store.delete_messages_by_session_id,
    "messageId": data_store.delete_message_by_message_id
}


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

    messages = None
    for arg_name, get_func in get_functions.items():
        if arg_name in request.args:
            arg_val = request.args.get(arg_name)
            transformation, err_msg = arg_transformations[arg_name]
            transformed_arg = transformation(arg_val)

            if transformed_arg is None:
                abort(400, err_msg)

            messages = get_func(transformed_arg)

    if messages is None:
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

    deleted_amount = None
    for arg_name, delete_func in delete_functions.items():
        if arg_name in request.args:
            arg_val = request.args.get(arg_name)
            transformation, err_msg = arg_transformations[arg_name]
            transformed_arg = transformation(arg_val)

            if transformed_arg is None:
                abort(400, err_msg)

            deleted_amount = delete_func(transformed_arg)

    if deleted_amount is None:
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
