"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from abc import ABC, abstractmethod
from typing import Type, Optional, TypeVar, Generic, List

from nomenclators_archetype.domain.repository.builders import Pageable

D = TypeVar('D', bound=object)  # Domain class representation
I = TypeVar('I', bound=object)  # Intentifier class representation
S = TypeVar('S', bound=object)  # Session class representation
R = TypeVar('R', bound=object)  # Repository class representation
M = TypeVar('M', bound=object)  # Mapper class representation


class BaseService(ABC, Generic[S]):  # type: ignore
    """BaseService class"""

    @abstractmethod
    def set_session(self, new_session: S):
        """Set session"""
        raise NotImplementedError


class NomenclatorService(BaseService, Generic[D, R, M]):  # type: ignore
    """NomenclatorService class"""

    def __init__(self, session: Optional[S] = None, repository: Optional[R] = None, mapper: Optional[Type[M]] = None):
        self._session = session
        self._repository = repository
        self._mapper = mapper

    @property
    def repository(self) -> R:
        """Get repository for nomenclator service class"""
        if not hasattr(self, "_repository") or self._repository is None:
            if hasattr(self, "_session") and self._session is not None:
                self._repository = self.get_repository()  # type: ignore
            else:
                raise NotImplementedError(
                    "The session class must be injected by constructor to get repository")
        return self._repository

    @property
    def mapper(self) -> Type[M]:
        """Get mapper for nomenclator service class"""
        if not hasattr(self, "_mapper") or self._mapper is None:
            self._mapper = self.get_mapper_class()  # type: ignore
        else:
            child_mapper = self.get_mapper_class()
            if issubclass(child_mapper, self._mapper) and child_mapper is not self._mapper:
                self._mapper = child_mapper  # type: ignore
        return self._mapper

    @property
    def entity_name(self) -> str:
        """Get entity name"""
        return self.repository.entity.__name__ if self.repository.entity else 'Undefined class'

    @property
    def repository_count(self):
        """Get count of items"""
        return self.repository.count()

    def set_session(self, new_session):
        """Set session"""
        self._session = new_session
        if hasattr(self, "_repository") and self._repository is not None:
            self._repository.set_session(new_session)  # type: ignore

    def get_repository(self) -> R:
        """Get repository for nomenclator service class"""
        raise NotImplementedError(
            "The repository class must be injected by constructor or implemented by subclasses")

    def get_mapper_class(self) -> Type[M]:
        """Get mapper for nomenclator service class"""
        raise NotImplementedError(
            "The mapper definition class must be injected by constructor or implemented by subclasses")

    def get_item_by_id(self, _id: I) -> D:  # type: ignore
        """Get item by id"""
        return self.mapper.map_from_entity_to_domain(  # type: ignore
            self.repository.get_by_id(_id)  # type: ignore
        )

    def list_items(self, pageable: Optional[Pageable] = None, filters: Optional[dict] = None,
                   group_by: Optional[list] = None, group_by_id: Optional[str] = None) -> List[D]:
        """
        Get list items.

        :param pageable: Pageable object
        :param filters: Filters object
        :param group_by: Group by object
        :param group_by_id: Group by id object
        """
        return [
            self.mapper.map_from_entity_to_domain(entity)  # type: ignore
            for entity in self.repository.get_all(  # type: ignore
                pageable, filters, group_by, group_by_id)
        ]

    def create_item(self, item: D) -> D:
        """Create a new item"""
        return self.mapper.map_from_entity_to_domain(  # type: ignore
            self.repository.create(  # type: ignore
                self.mapper.map_from_domain_to_entity(item)  # type: ignore
            )
        )

    def update_item(self, item: D) -> D:
        """Update an item"""
        return self.mapper.map_from_entity_to_domain(  # type: ignore
            self.repository.update(  # type: ignore
                self.mapper.map_from_domain_to_entity(item)  # type: ignore
            )
        )

    def update_by_id(self, _id: I, item: D) -> D:  # type: ignore
        """Update an item by id"""
        return self.mapper.map_from_entity_to_domain(  # type: ignore
            self.repository.update_by_id(  # type: ignore
                _id, self.mapper.map_from_domain_to_entity(  # type: ignore
                    item)
            )
        )

    def delete_item(self, item: D):
        """Delete an item"""
        self.repository.delete_by_id(  # type: ignore
            item.id  # type: ignore
        )

    def delete_by_id(self, _id: I):  # type: ignore
        """Delete an item by id"""
        self.repository.delete_by_id(_id)  # type: ignore

    def find_by_spec(self, spec, pageable: Optional[Pageable] = None) -> List[D]:
        """Allows dynamic queries based on criteria."""
        return [
            self.mapper.map_from_entity_to_domain(entity)  # type: ignore
            for entity in self.repository.find_by_spec(  # type: ignore
                spec, pageable)
        ]
