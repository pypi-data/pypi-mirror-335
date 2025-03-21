# -*- coding: utf-8 -*-
from pip_services4_components.config import ConfigParams
from pip_services4_components.refer import References, Descriptor
from pip_services4_data.query import PagingParams, FilterParams

from aichatconnect.modelmultiplexor.data import Modelmultiplexor
from aichatconnect.modelmultiplexor.logic.ModelmultiplexorsService import ModelmultiplexorsService
from aichatconnect.modelmultiplexor.persistence.ModelmultiplexorsMemoryPersistence import ModelmultiplexorsMemoryPersistence

MODEL_MULTIPLEXOR1 = Modelmultiplexor(
    id='1',
    name='00001',
    type="Type1",
    site_id='1',
    content='ABC'
)

MODEL_MULTIPLEXOR2 = Modelmultiplexor(
    id='2',
    name='00002',
    type="Type2",
    site_id='1',
    content='XYZ'
)


class TestModelmultiplexorsService:
    persistence: ModelmultiplexorsMemoryPersistence
    service: ModelmultiplexorsService

    def setup_method(self):
        self.persistence = ModelmultiplexorsMemoryPersistence()
        self.persistence.configure(ConfigParams())

        self.service = ModelmultiplexorsService()
        self.service.configure(ConfigParams())

        references = References.from_tuples(
            Descriptor('aichatconnect-modelmultiplexors', 'persistence', 'memory', 'default', '1.0'), self.persistence,
            Descriptor('aichatconnect-modelmultiplexors', 'service', 'default', 'default', '1.0'), self.service
        )

        self.service.set_references(references)

        self.persistence.open(None)

    def teardown_method(self):
        self.persistence.close(None)

    def test_crud_operations(self):
        # Create the first model
        model = self.service.create_model(None, MODEL_MULTIPLEXOR1)
        assert MODEL_MULTIPLEXOR1.name == model.name
        assert MODEL_MULTIPLEXOR1.site_id == model.site_id
        assert MODEL_MULTIPLEXOR1.type == model.type
        assert model.content is not None

        # Create the second model
        model = self.service.create_model(None, MODEL_MULTIPLEXOR2)
        assert MODEL_MULTIPLEXOR2.name == model.name
        assert MODEL_MULTIPLEXOR2.site_id == model.site_id
        assert MODEL_MULTIPLEXOR2.type == model.type
        assert model.content is not None

        # Get all models
        page = self.service.get_models(None, FilterParams(), PagingParams())
        assert page is not None
        assert len(page.data) == 2

        model1: Modelmultiplexor = page.data[0]

        # Update the model
        model1.name = 'ABC'

        model = self.service.update_model(None, model1)
        assert model1.id == model.id
        assert 'ABC' == model.name

        # Get model by name
        model = self.service.get_model_by_name(None, model1.name)
        assert model1.id == model.id

        # Delete the model
        model = self.service.delete_model_by_id(None, model1.id)
        assert model1.id == model.id

        # Try to get deleted model
        model = self.service.get_model_by_id(None, model1.id)
        assert model is None
