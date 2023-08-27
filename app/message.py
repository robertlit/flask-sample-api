from dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    application_id: int
    session_id: str
    message_id: str
    participants: list
    content: str
