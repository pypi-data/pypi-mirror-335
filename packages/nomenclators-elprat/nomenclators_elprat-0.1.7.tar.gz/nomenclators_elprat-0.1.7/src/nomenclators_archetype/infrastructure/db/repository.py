"""
----------------------------------------------------------------------------------------------------
Written by Yovany Dominico Girón (y.dominico.giron@elprat.cat) for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from typing import Type, Union, Optional

from sqlalchemy import event
from sqlalchemy.orm import Session

from nomenclators_archetype.domain.repository.commons import JpaRepository
from nomenclators_archetype.domain.repository.builders import QueryBuilder

from nomenclators_archetype.infrastructure.db.commons import entity2dict
from nomenclators_archetype.infrastructure.db.commons import BaseSimpleNomenclator
from nomenclators_archetype.infrastructure.db.commons import BaseNomenclator
from nomenclators_archetype.infrastructure.db.commons import TreeNomenclator

from nomenclators_archetype.infrastructure.db.builders import QueryBuilderImpl

NomenclatorId = Union[int, str]


class BaseSimpleNomenclatorRepository(JpaRepository[NomenclatorId, BaseSimpleNomenclator, Session, QueryBuilder]):
    """BaseSimpleNomenclator Repository Class"""

    def __init__(self, session: Optional[Session] = None, builder: Optional[QueryBuilder] = None):
        super().__init__(session, builder, BaseSimpleNomenclator)
        self._session = session
        self._builder = builder

    def get_entity_model_class(self) -> Type[BaseSimpleNomenclator]:
        """Get persistence type class"""
        raise NotImplementedError(
            "The entity model definition must be injected by constructor or implemented by subclasses")

    def get_query_builder(self) -> QueryBuilder:
        return QueryBuilderImpl()

    def mapper_entity_to_dict(self, entity: BaseSimpleNomenclator) -> dict:
        """Transform an entity to a dictionary."""
        return entity2dict(entity, ['id'])


class BaseNomenclatorRepository(JpaRepository[NomenclatorId, BaseNomenclator, Session, QueryBuilder]):
    """BaseNomenclator Repository Class"""

    def __init__(self, session: Optional[Session] = None, builder: Optional[QueryBuilder] = None):
        super().__init__(session, builder, BaseNomenclator)
        self._session = session
        self._builder = builder

    def get_entity_model_class(self) -> Type[BaseNomenclator]:
        """Get persistence type class"""
        raise NotImplementedError(
            "The entity model definition must be injected by constructor or implemented by subclasses")

    def get_query_builder(self) -> QueryBuilder:
        return QueryBuilderImpl()

    def mapper_entity_to_dict(self, entity: BaseNomenclator) -> dict:
        """Transform an entity to a dictionary."""
        return entity2dict(entity, ['id'])


@event.listens_for(Session, "before_flush")
def soft_delete_listener(session, flush_context, instances):  # pylint: disable=unused-argument
    """Soft delete listener"""

    for obj in session.deleted:
        if (
            isinstance(obj, (
                BaseSimpleNomenclator,
                BaseNomenclator,
                TreeNomenclator
            ))
        ) and obj.active:
            obj.active = False
            session.add(obj)
