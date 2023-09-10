from dataclasses import fields
from typing import Optional, Tuple

from app.message import Message

required_fields = [(field.name, field.type) for field in fields(Message)]


def validate_message_data(data) -> Tuple[bool, Optional[str]]:
    for field_name, field_type in required_fields:
        if field_name not in data:
            return False, f"Missing {field_name}"

        if not isinstance(data[field_name], field_type):
            return False, f"Invalid type for {field_name}: {field_type.__name__} expected"

    return True, None
