# -*- coding: utf-8 -*-
import os

import pytest
from pip_services4_components.config import ConfigParams

from aichatconnect.modelmultiplexor.persistence import ModelmultiplexorsMongoDbPersistence
from test.modelmultiplexor.persistence.ModelmultiplexorsPersistenceFixture import ModelmultiplexorsPersistenceFixture

mongodb_uri = os.environ.get('MONGO_SERVICE_URI')
mongodb_host = os.environ.get('MONGO_SERVICE_HOST') or 'localhost'
mongodb_port = os.environ.get('MONGO_SERVICE_PORT') or 27017
mongodb_database = os.environ.get('MONGO_SERVICE_DB') or 'test'


@pytest.mark.skipif(not mongodb_uri and not mongodb_host, reason="MongoDb connection is not set")
class TestModelmultiplexorsMongoDbPersistence:
    persistence: ModelmultiplexorsMongoDbPersistence
    fixture: ModelmultiplexorsPersistenceFixture

    def setup_method(self):
        self.persistence = ModelmultiplexorsMongoDbPersistence()
        self.persistence.configure(ConfigParams.from_tuples(
            'connection.uri', mongodb_uri,
            'connection.host', mongodb_host,
            'connection.port', mongodb_port,
            'connection.database', mongodb_database,
        ))

        self.fixture = ModelmultiplexorsPersistenceFixture(self.persistence)

        self.persistence.open(None)
        self.persistence.clear(None)

    def teardown_method(self):
        self.persistence.close(None)

    def test_crud_operations(self):
        self.fixture.test_crud_operations()

    def test_get_with_filters(self):
        self.fixture.test_get_with_filters()