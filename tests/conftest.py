import os

import pytest

from app.api import create_app
from app.data import DiskDataStore


@pytest.fixture
def data_store():
    db_file_name = "database.db"
    data_store = DiskDataStore(db_file_name)

    yield data_store

    data_store.con.close()
    os.remove(db_file_name)


@pytest.fixture
def app(data_store):
    return create_app(data_store)


@pytest.fixture
def client(app):
    return app.test_client()
