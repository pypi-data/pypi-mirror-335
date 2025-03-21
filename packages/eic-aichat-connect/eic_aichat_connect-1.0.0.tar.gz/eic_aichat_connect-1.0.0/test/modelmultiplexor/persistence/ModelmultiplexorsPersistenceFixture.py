# -*- coding: utf-8 -*-
from pip_services4_data.query import FilterParams, PagingParams

from aichatconnect.modelmultiplexor.data.Modelmultiplexor import Modelmultiplexor
from aichatconnect.modelmultiplexor.persistence.IModelmultiplexorsPersistence import IModelmultiplexorsPersistence

MODEL_MULTIPLEXOR1 = Modelmultiplexor(
    id='1',
    name='00001',
    type="Type1",
    site_id='1',
    content='ABC'
)

MODEL_MULTIPLEXOR2 = Modelmultiplexor(
    id='2',
    name='00001',
    type="Type2",
    site_id='1',
    content='XYZ'
)

MODEL_MULTIPLEXOR3 = Modelmultiplexor(
    id='3',
    name='00002',
    type="Type1",
    site_id='2',
    content='DEF'
)


class ModelmultiplexorsPersistenceFixture:
    _persistence: IModelmultiplexorsPersistence

    def __init__(self, persistence: IModelmultiplexorsPersistence):
        assert persistence is not None
        self._persistence = persistence

    def test_create_modelmultiplexors(self):
        # Create the first model
        model = self._persistence.create(None, MODEL_MULTIPLEXOR1)
        assert MODEL_MULTIPLEXOR1.name == model.name
        assert MODEL_MULTIPLEXOR1.site_id == model.site_id
        assert MODEL_MULTIPLEXOR1.type == model.type
        assert model.content is not None

        # Create the second model
        model = self._persistence.create(None, MODEL_MULTIPLEXOR2)
        assert MODEL_MULTIPLEXOR2.name == model.name
        assert MODEL_MULTIPLEXOR2.site_id == model.site_id
        assert MODEL_MULTIPLEXOR2.type == model.type
        assert model.content is not None

        # Create the third model
        model = self._persistence.create(None, MODEL_MULTIPLEXOR3)
        assert MODEL_MULTIPLEXOR3.name == model.name
        assert MODEL_MULTIPLEXOR3.site_id == model.site_id
        assert MODEL_MULTIPLEXOR3.type == model.type
        assert model.content is not None

    def test_crud_operations(self):
        # Create items
        self.test_create_modelmultiplexors()

        # Get all models
        page = self._persistence.get_page_by_filter(None, FilterParams(), PagingParams())
        assert page is not None
        assert len(page.data) == 3

        model1: Modelmultiplexor = page.data[0]

        # Update the model
        model1.name = 'ABC'

        model = self._persistence.update(None, model1)
        assert model1.id == model.id
        assert 'ABC' == model.name

        # Get model by name
        model = self._persistence.get_one_by_name(None, model1.name)
        assert model1.id == model.id

        # Delete the model
        model = self._persistence.delete_by_id(None, model1.id)
        assert model1.id == model.id

        # Try to get deleted model
        model = self._persistence.get_one_by_id(None, model1.id)
        assert model is None

    def test_get_with_filters(self):
        # Create items
        self.test_create_modelmultiplexors()

        # Filter by id
        page = self._persistence.get_page_by_filter(None, FilterParams.from_tuples('id', '1'), PagingParams())
        assert len(page.data) == 1

        # Filter by name
        page = self._persistence.get_page_by_filter(None,
                                                    FilterParams.from_tuples('names', '00001,00003'),
                                                    PagingParams())
        assert len(page.data) == 2

        # Filter by site_id
        page = self._persistence.get_page_by_filter(None,
                                                    FilterParams.from_tuples('site_id', '1'),
                                                    PagingParams())
        assert len(page.data) == 2
