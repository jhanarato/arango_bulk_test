import pytest
from arango import ArangoClient
from arango.database import Database

DB_NAME = 'bulk_load_test'

@pytest.fixture
def client() -> ArangoClient:
    return ArangoClient(host="old-arango-db", port=8529, username='root', password='test')


@pytest.fixture
def database(client):
    client.create_database(DB_NAME)
    yield
    client.delete_database(DB_NAME)

def test_database(client, database):
    assert DB_NAME in client.databases()