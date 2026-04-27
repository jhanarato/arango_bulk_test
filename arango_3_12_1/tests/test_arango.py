import pytest
from arango import ArangoClient
from arango.database import Database

DB_NAME = 'bulk_load_test'

@pytest.fixture
def client() -> ArangoClient:
    return ArangoClient(host='old-arango-db', port=8529, username='root', password='test')


@pytest.fixture
def database(client):
    client.create_database(DB_NAME)
    yield client.database(DB_NAME)
    client.delete_database(DB_NAME)

def test_database(database):
    assert database.name == DB_NAME

class TestImportBulk:
    def test_populate_a_collection(self, database):
        cats_collection = database.create_collection('cats')
        cats = [
            {
                "_key": "felicity",
                "name": "Felicity",
                "breed": "Siamese",
            },
            {
                "_key": "prince",
                "name": "Prince",
                "breed": "Shorthair",
            },

        ]
        cats_collection.import_bulk(cats)
        assert cats_collection.count() == 2
