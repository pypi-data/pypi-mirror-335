# -*- coding: utf-8 -*-
from pip_services4_components.config import ConfigParams
from pip_services4_components.refer import References, Descriptor
from pip_services4_data.query import PagingParams, FilterParams

from aichatmodels.basemodels.data import BaseModel
from aichatmodels.basemodels.logic import BaseModelsService
from aichatmodels.basemodels.persistence import BaseModelsMemoryPersistence

BASE_MODEL1 = BaseModel(
    id='1',
    name='00001',
    type="Type1",
    site_id='1',
    content='ABC'
)

BASE_MODEL2 = BaseModel(
    id='2',
    name='00002',
    type="Type2",
    site_id='1',
    content='XYZ'
)


class TestBaseModelsService:
    persistence: BaseModelsMemoryPersistence
    service: BaseModelsService

    def setup_method(self):
        self.persistence = BaseModelsMemoryPersistence()
        self.persistence.configure(ConfigParams())

        self.service = BaseModelsService()
        self.service.configure(ConfigParams())

        references = References.from_tuples(
            Descriptor('aichatmodels-basemodels', 'persistence', 'memory', 'default', '1.0'), self.persistence,
            Descriptor('aichatmodels-basemodels', 'service', 'default', 'default', '1.0'), self.service
        )

        self.service.set_references(references)

        self.persistence.open(None)

    def teardown_method(self):
        self.persistence.close(None)

    def test_crud_operations(self):
        # Create the first model
        model = self.service.create_model(None, BASE_MODEL1)
        assert BASE_MODEL1.name == model.name
        assert BASE_MODEL1.site_id == model.site_id
        assert BASE_MODEL1.type == model.type
        assert model.content is not None

        # Create the second model
        model = self.service.create_model(None, BASE_MODEL2)
        assert BASE_MODEL2.name == model.name
        assert BASE_MODEL2.site_id == model.site_id
        assert BASE_MODEL2.type == model.type
        assert model.content is not None

        # Get all models
        page = self.service.get_models(None, FilterParams(), PagingParams())
        assert page is not None
        assert len(page.data) == 2

        model1: BaseModel = page.data[0]

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
