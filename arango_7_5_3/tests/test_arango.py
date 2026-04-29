from typing import Any, Generator

import pytest
from arango import ArangoClient, DocumentInsertError
from arango.collection import StandardCollection
from arango.database import StandardDatabase

DB_NAME = 'bulk_load_test'


@pytest.fixture
def client() -> ArangoClient:
    return ArangoClient()


@pytest.fixture
def sys_db(client) -> StandardDatabase:
    return client.db('_system', username='root', password='test')


@pytest.fixture
def database(client, sys_db) -> Generator[StandardDatabase, Any, None]:
    if sys_db.has_database(DB_NAME):
        sys_db.delete_database(DB_NAME)
    sys_db.create_database(DB_NAME)
    yield client.db(DB_NAME, username='root', password='test')


@pytest.fixture
def cats_collection(database) -> StandardCollection:
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

    def test_fails_does_not_fail_silently_by_default(self, cats_collection, duplicates):
        with pytest.raises(DocumentInsertError):
            cats_collection.import_bulk(duplicates)

    def test_gives_error_when_halt_on_error(self, cats_collection, duplicates):
        with pytest.raises(DocumentInsertError):
            cats_collection.import_bulk(duplicates, halt_on_error=True)

    def test_error_has_no_context(self, cats_collection, duplicates):
        try:
            cats_collection.import_bulk(duplicates, halt_on_error=True)
        except DocumentInsertError as e:
            assert str(e) == '[HTTP 409][ERR 1210] unique constraint violated'
