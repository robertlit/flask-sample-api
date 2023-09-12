import json
from typing import Callable, Dict, Any, List

from flask import Flask, request, abort
from werkzeug.exceptions import HTTPException

from app.data import DataStore
from app.message import Message
from app.parsing import parse_int_arg, identity_arg
from app.validation import validate_message_data


def create_app(data_store: DataStore) -> Flask:
    app = Flask(__name__)

    arg_transformations: Dict[str, Callable[[str, str], Any]] = {
        "applicationId": parse_int_arg,
        "sessionId": identity_arg,
        "messageId": identity_arg
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
            abort(400, f"Message with {message.message_id=} already exists")

        data_store.add_message(message)
        return {
            "result": "Message added successfully"
        }

    @app.get("/GetMessage")
    def get_message():
        if len(request.args.keys()) != 1:
            abort(400, f"Specify exactly one of the following: {', '.join(get_functions.keys())}")

        arg_name = next(iter(request.args.keys()))

        if arg_name not in get_functions:
            abort(400, f"Specify one of the following: {', '.join(get_functions.keys())}")

        arg_val = request.args[arg_name]
        arg_val, error_message = arg_transformations[arg_name](arg_val, arg_name)

        if arg_val is None:
            abort(400, error_message)

        messages = get_functions[arg_name](arg_val)

        if len(messages) == 0:
            abort(404, "No messages found")

        return {
            "messages": messages
        }

    @app.delete("/DeleteMessage")
    def delete_message():
        if len(request.args.keys()) != 1:
            abort(400, f"Specify exactly one of the following: {', '.join(delete_functions.keys())}")

        arg_name = next(iter(request.args.keys()))

        if arg_name not in delete_functions:
            abort(400, f"Specify one of the following: {', '.join(delete_functions.keys())}")

        arg_val = request.args[arg_name]
        arg_val, error_message = arg_transformations[arg_name](arg_val, arg_name)

        if arg_val is None:
            abort(400, error_message)

        deleted_amount = delete_functions[arg_name](arg_val)

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

    return app
