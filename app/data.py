import json
import sqlite3
from abc import ABC, abstractmethod
from collections import defaultdict

from app.message import Message


class DataStore(ABC):

    @abstractmethod
    def add_message(self, message: Message) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_messages_by_application_id(self, application_id: int) -> list[Message]:
        raise NotImplementedError

    @abstractmethod
    def get_messages_by_session_id(self, session_id: str) -> list[Message]:
        raise NotImplementedError

    @abstractmethod
    def get_message_by_message_id(self, message_id: str) -> Message | None:
        raise NotImplementedError

    @abstractmethod
    def delete_messages_by_application_id(self, application_id: int) -> int:
        raise NotImplementedError

    @abstractmethod
    def delete_messages_by_session_id(self, session_id: str) -> int:
        raise NotImplementedError

    @abstractmethod
    def delete_message_by_message_id(self, message_id: str) -> int:
        raise NotImplementedError


class MemoryDataStore(DataStore):
    """
    In-memory data storage.
    This implementation uses three dicts for constant lookup time with all three parameters.
    """

    def __init__(self):
        self.__by_application_id: dict[int, list[Message]] = defaultdict(list)
        self.__by_session_id: dict[str, list[Message]] = defaultdict(list)
        self.__by_message_id: dict[str, Message] = dict()

    def add_message(self, message: Message) -> None:
        self.__by_application_id[message.application_id].append(message)
        self.__by_session_id[message.session_id].append(message)
        self.__by_message_id[message.message_id] = message

    def get_messages_by_application_id(self, application_id: int) -> list[Message]:
        return self.__by_application_id[application_id]

    def get_messages_by_session_id(self, session_id: str) -> list[Message]:
        return self.__by_session_id[session_id]

    def get_message_by_message_id(self, message_id: str) -> Message | None:
        return self.__by_message_id.get(message_id)

    def delete_messages_by_application_id(self, application_id: int) -> int:
        for message in self.__by_application_id[application_id]:
            self.__by_session_id[message.session_id].remove(message)
            self.__by_message_id.pop(message.message_id)

        deleted_amount = len(self.__by_application_id[application_id])
        self.__by_application_id[application_id].clear()
        return deleted_amount

    def delete_messages_by_session_id(self, session_id: str) -> int:
        for message in self.__by_session_id[session_id]:
            self.__by_application_id[message.application_id].remove(message)
            self.__by_message_id.pop(message.message_id)

        deleted_amount = len(self.__by_session_id[session_id])
        self.__by_session_id[session_id].clear()
        return deleted_amount

    def delete_message_by_message_id(self, message_id: str) -> int:
        message = self.__by_message_id.get(message_id)

        if message:
            self.__by_application_id[message.application_id].remove(message)
            self.__by_session_id[message.session_id].remove(message)
            self.__by_message_id.pop(message_id)
            return 1

        return 0


class DiskDataStore(DataStore):
    """SQLite data storage."""

    def __init__(self, db_file_name="database.db"):
        self.db_file_name = db_file_name
        create_table_query = """
            CREATE TABLE IF NOT EXISTS messages (
                application_id INTEGER,
                session_id TEXT,
                message_id TEXT PRIMARY KEY,
                participants TEXT,
                content TEXT
            );
        """
        con = self.get_connection()
        con.execute(create_table_query)
        con.commit()
        con.close()

    def get_connection(self):
        return sqlite3.connect(self.db_file_name)

    def add_message(self, message: Message) -> None:
        insert_query = """
            INSERT INTO messages 
            VALUES (?, ?, ?, ?, ?);
        """
        con = self.get_connection()
        ser_participants = json.dumps(message.participants)
        con.execute(insert_query, (
            message.application_id,
            message.session_id,
            message.message_id,
            ser_participants,
            message.content
        ))
        con.commit()
        con.close()

    def get_messages_by_application_id(self, application_id: int) -> list[Message]:
        select_query = """
            SELECT * FROM messages
            WHERE application_id = ?;
        """
        result = []
        con = self.get_connection()
        cur = con.cursor()
        cur.execute(select_query, (application_id,))
        for row in cur:
            row = list(row)
            row[3] = json.loads(row[3])
            result.append(Message(*row))

        con.close()
        return result

    def get_messages_by_session_id(self, session_id: str) -> list[Message]:
        select_query = """
            SELECT * FROM messages
            WHERE session_id = ?;
        """
        result = []
        con = self.get_connection()
        cur = con.cursor()
        cur.execute(select_query, (session_id,))
        for row in cur:
            row = list(row)
            row[3] = json.loads(row[3])
            result.append(Message(*row))

        con.close()
        return result

    def get_message_by_message_id(self, message_id: str) -> Message | None:
        select_query = """
            SELECT * FROM messages
            WHERE message_id = ?;
        """
        con = self.get_connection()
        cur = con.cursor()
        cur.execute(select_query, (message_id,))

        row = cur.fetchone()
        if row is None:
            return None

        row = list(row)
        row[3] = json.loads(row[3])

        con.close()
        return Message(*row)

    def delete_messages_by_application_id(self, application_id: int) -> int:
        delete_query = """
            DELETE FROM messages
            WHERE application_id = ?;
        """
        con = self.get_connection()
        cur = con.cursor()

        cur.execute(delete_query, (application_id,))
        con.commit()
        con.close()
        return cur.rowcount

    def delete_messages_by_session_id(self, session_id: str) -> int:
        delete_query = """
            DELETE FROM messages
            WHERE session_id = ?;
        """
        con = self.get_connection()
        cur = con.cursor()

        cur.execute(delete_query, (session_id,))
        con.commit()
        con.close()
        return cur.rowcount

    def delete_message_by_message_id(self, message_id: str) -> int:
        delete_query = """
            DELETE FROM messages
            WHERE message_id = ?;
        """
        con = self.get_connection()
        cur = con.cursor()

        cur.execute(delete_query, (message_id,))
        con.commit()
        con.close()
        return cur.rowcount
