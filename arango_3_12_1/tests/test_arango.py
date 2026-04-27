import pytest
from arango import ArangoClient
from arango.exceptions import DocumentInsertError

DB_NAME = 'bulk_load_test'

@pytest.fixture
def client() -> ArangoClient:
    return ArangoClient(host='old-arango-db', port=8529, username='root', password='test')


@pytest.fixture
def database(client):
    client.create_database(DB_NAME)
    yield client.database(DB_NAME)
    client.delete_database(DB_NAME)

@pytest.fixture
def cats_collection(database):
    return database.create_collection('cats')

@pytest.fixture
def cats():
    return [
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

@pytest.fixture
def duplicates():
    return [
        {
            "_key": "felicity",
            "name": "Felicity",
            "breed": "Siamese",
        },
        {
            "_key": "felicity",
            "name": "Felicity",
            "breed": "Siamese",
        },
    ]

class TestImportBulk:
    def test_populate_a_collection(self, cats_collection, cats):
        cats_collection.import_bulk(cats)
        assert cats_collection.count() == 2

    def test_fails_silently_by_default(self, cats_collection, duplicates):
        cats_collection.import_bulk(duplicates)
        assert cats_collection.count() == 1

    def test_gives_error_when_halt_on_error(self, cats_collection, duplicates):
        with pytest.raises(DocumentInsertError):
            cats_collection.import_bulk(duplicates, halt_on_error=True)