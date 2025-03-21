# -*- coding: utf-8 -*-
from aichatconnect.modelmultiplexor.persistence import ModelmultiplexorsMemoryPersistence
from test.modelmultiplexor.persistence.ModelmultiplexorsPersistenceFixture import ModelmultiplexorsPersistenceFixture


class TestModelmultiplexorsMemoryPersistence:
    persistence: ModelmultiplexorsMemoryPersistence
    fixture: ModelmultiplexorsPersistenceFixture

    def setup_method(self):
        self.persistence = ModelmultiplexorsMemoryPersistence()

        self.fixture = ModelmultiplexorsPersistenceFixture(self.persistence)

        self.persistence.open(None)
        self.persistence.clear(None)

    def teardown_method(self):
        self.persistence.close(None)

    def test_crud_operations(self):
        self.fixture.test_crud_operations()

    def test_get_with_filters(self):
        self.fixture.test_get_with_filters()