# -*- coding: utf-8 -*-
from pip_services4_data.query import FilterParams, PagingParams

from aichatmodels.basemodels.data.BaseModel import BaseModel
from aichatmodels.basemodels.persistence.IBaseModelsPersistence import IBaseModelsPersistence

BASE_MODEL1 = BaseModel(
    id='1',
    name='00001',
    type="Type1",
    site_id='1',
    content='ABC'
)

BASE_MODEL2 = BaseModel(
    id='2',
    name='00001',
    type="Type2",
    site_id='1',
    content='XYZ'
)

BASE_MODEL3 = BaseModel(
    id='3',
    name='00002',
    type="Type1",
    site_id='2',
    content='DEF'
)


class BaseModelsPersistenceFixture:
    _persistence: IBaseModelsPersistence

    def __init__(self, persistence: IBaseModelsPersistence):
        assert persistence is not None
        self._persistence = persistence

    def test_create_base_models(self):
        # Create the first model
        entity = self._persistence.create(None, BASE_MODEL1)
        assert BASE_MODEL1.name == entity.name
        assert BASE_MODEL1.site_id == entity.site_id
        assert BASE_MODEL1.type == entity.type
        assert entity.content is not None

        # Create the second model
        entity = self._persistence.create(None, BASE_MODEL2)
        assert BASE_MODEL2.name == entity.name
        assert BASE_MODEL2.site_id == entity.site_id
        assert BASE_MODEL2.type == entity.type
        assert entity.content is not None

        # Create the third model
        entity = self._persistence.create(None, BASE_MODEL3)
        assert BASE_MODEL3.name == entity.name
        assert BASE_MODEL3.site_id == entity.site_id
        assert BASE_MODEL3.type == entity.type
        assert entity.content is not None

    def test_crud_operations(self):
        # Create items
        self.test_create_base_models()

        # Get all models
        page = self._persistence.get_page_by_filter(None, FilterParams(), PagingParams())
        assert page is not None
        assert len(page.data) == 3

        entity1: BaseModel = page.data[0]

        # Update the model
        entity1.name = 'ABC'

        entity = self._persistence.update(None, entity1)
        assert entity1.id == entity.id
        assert 'ABC' == entity.name

        # Get model by name
        entity = self._persistence.get_one_by_name(None, entity1.name)
        assert entity1.id == entity.id

        # Delete the model
        entity = self._persistence.delete_by_id(None, entity1.id)
        assert entity1.id == entity.id

        # Try to get deleted model
        entity = self._persistence.get_one_by_id(None, entity1.id)
        assert entity is None

    def test_get_with_filters(self):
        # Create items
        self.test_create_base_models()

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
