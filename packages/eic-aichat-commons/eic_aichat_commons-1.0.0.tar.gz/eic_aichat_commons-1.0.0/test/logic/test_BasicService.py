# -*- coding: utf-8 -*-
from pip_services4_commons.config import ConfigParams
from pip_services4_commons.data import FilterParams, PagingParams
from pip_services4_commons.refer import References, Descriptor

from service_basic_pipservices.data import EntityTypeV1
from service_basic_pipservices.data import EntityV1
from service_basic_pipservices.logic import BasicService

ENTITY1 = EntityV1(id='1',
                   name='00001',
                   type=EntityTypeV1.Type1,
                   site_id='1',
                   content='ABC')

ENTITY2 = EntityV1(id='2',
                   name='00002',
                   type=EntityTypeV1.Type2,
                   site_id='1',
                   content='XYZ')


class TestBasicService:
    service: BasicService

    def setup_method(self):
        self.service = BasicService()
        self.service.configure(ConfigParams())

        references = References.from_tuples(
            Descriptor('service-basic', 'service', 'default', 'default', '1.0'), self.service
        )

        self.service.set_references(references)

    def test_crud_operations(self):
        # Create the first entity
        entity = self.service.create_entity(None, ENTITY1)
        assert ENTITY1.name == entity.name
        assert ENTITY1.site_id == entity.site_id
        assert ENTITY1.type == entity.type
        assert ENTITY1.name == entity.name
        assert entity.content is not None

        # Create the second entity
        entity = self.service.create_entity(None, ENTITY2)
        assert ENTITY2.name == entity.name
        assert ENTITY2.site_id == entity.site_id
        assert ENTITY2.type == entity.type
        assert ENTITY2.name == entity.name
        assert entity.content is not None

        # Get all entities
        page = self.service.get_entities(None, FilterParams(), PagingParams())
        assert page is not None
        assert len(page.data) == 2

        entity1: EntityV1 = page.data[0]

        # Update the entity
        entity1.name = 'ABC'

        entity = self.service.update_entity(None, entity1)
        assert entity1.id == entity.id
        assert 'ABC' == entity.name

        # Get entity by name
        entity = self.service.get_entity_by_name(None, entity1.name)
        assert entity1.id == entity.id

        # Delete the entity
        entity = self.service.delete_entity_by_id(None, entity1.id)
        assert entity1.id == entity.id

        # Try to get deleted entity
        entity = self.service.get_entity_by_id(None, entity1.id)
        assert entity is None
