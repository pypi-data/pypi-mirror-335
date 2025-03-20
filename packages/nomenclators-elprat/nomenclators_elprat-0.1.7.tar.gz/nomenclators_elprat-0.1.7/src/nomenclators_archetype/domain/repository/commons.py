"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from abc import abstractmethod
from typing import Type, Optional, TypeVar, Protocol, List

from nomenclators_archetype.domain.loggers import default_logger
from nomenclators_archetype.domain.repository.builders import Pageable

I = TypeVar('I', bound=object)  # Intentifier class representation
E = TypeVar('E', bound=object)  # Persistence Entity class representation
S = TypeVar('S', bound=object)  # Session class representation
B = TypeVar('B', bound=object)  # Query Builder class representation


class RepositoryIntegrityError(Exception):
    """RepositoryIntegrityError exception Class"""


class RepositoryMissingElementError(Exception):
    """RepositoryMissingElementError exception Class"""

    def __init__(self, missing_id: str, message: str):
        super().__init__(f"Entity with ID: {missing_id} {message}")


class CrudRepository(Protocol[I, E, S, B]):  # type: ignore
    """CrudRepository Class"""

    _session: Optional[S]
    _builder: Optional[B]
    _entity: Optional[Type[E]]

    def __init__(self, session: Optional[S], builder: Optional[B], entity: Optional[Type[E]] = None):
        pass

    @property
    def session(self) -> S:
        """Get session"""
        if self._session:
            return self._session
        else:
            raise NotImplementedError(
                "The session must be injected on the class by constructor or setter")

    def set_session(self, new_session):
        """Set session"""
        self._session = new_session

    @property
    def builder(self) -> B:
        """Get builder"""
        if not hasattr(self, "_builder") or self._builder is None:
            self._builder = self.get_query_builder()
        return self._builder.initializate()

    @property
    def entity(self) -> Type[E]:
        """Get entity"""
        if not hasattr(self, "_entity") or self._entity is None:
            self._entity = self.get_entity_model_class()
        else:
            child_model = self.get_entity_model_class()
            if issubclass(child_model, self._entity) and child_model is not self._entity:
                self._entity = child_model

        return self._entity

    def get_entity_model_class(self) -> Type[E]:
        """Get persistence type class"""
        raise NotImplementedError(
            "The entity model definition must be injected by constructor or implemented by subclasses")

    def get_query_builder(self) -> B:
        """Get query builder operator for repository class"""
        raise NotImplementedError(
            "The query_builder class must be injected by constructor or implemented by subclasses")

    def count(self):
        """Get total numbers of entities."""
        query = self.create_builder().set_filter({'active': True}).build()
        return query.count()

    def save(self, entity: E) -> E:
        """Save an entity (create or update)."""
        try:
            self.session.add(entity)  # type: ignore
            return entity
        except Exception as ex:  # pylint: disable=broad-except
            default_logger.exception("Error on save operation")
            raise RepositoryIntegrityError("Error on save operation") from ex

    def update(self, updated_entity: E) -> E:
        """Update an entity."""
        entity = self.get_by_id_lazy_select(
            updated_entity.id)  # type: ignore

        if not entity:
            default_logger.exception(
                "Entity %s, not fount", updated_entity.id)
            raise RepositoryMissingElementError(
                str(updated_entity.id), "not found")
        if not entity.active:  # type: ignore
            default_logger.error(
                "Entity %s, cannot be updated", updated_entity.id)
            raise RepositoryMissingElementError(
                str(updated_entity.id), "cannot be updated")  # type: ignore

        try:
            return self.session.merge(updated_entity)  # type: ignore
        except Exception as ex:  # pylint: disable=broad-except
            default_logger.exception("Error on update operation")
            raise RepositoryIntegrityError("Error on update operation") from ex

    def update_by_id(self, _id: I, updated_entity: E):
        """Update an entity by its id."""
        entity = self.get_by_id(_id)
        if not entity:
            default_logger.error("Entity %s, not found", _id)
            raise RepositoryMissingElementError(str(_id), "not found")
        elif not entity.active:  # type: ignore
            default_logger.error("Entity %s, cannot be updated", _id)
            raise RepositoryMissingElementError(
                str(_id), "cannot be updated")  # type: ignore

        try:
            changes = self.mapper_entity_to_dict(updated_entity)

            for field, value in changes.items():
                if hasattr(entity, field) and value is not None:
                    setattr(entity, field, value)
        except Exception as ex:  # pylint: disable=broad-except
            default_logger.exception("Error on update operation")
            raise RepositoryIntegrityError("Error on update operation") from ex

    def delete(self, entity: E):
        """Remove of an entity."""
        if not entity:
            default_logger.error(
                "Operation delete not permit on entity undefined")
            raise RepositoryIntegrityError(
                "Operation delete not permit on entity undefined")
        elif not entity.active:  # type: ignore
            default_logger.error("Entity %s, cannot be deleted", entity.id)
            raise RepositoryMissingElementError(
                str(entity.id), "cannot be deleted")  # type: ignore

        try:
            entity.active = False  # type: ignore
            self.save(entity)
            self.session.flush()  # type: ignore
        except Exception as ex:  # pylint: disable=broad-except
            default_logger.exception("Error on delete operation")
            raise RepositoryIntegrityError("Error on delete operation") from ex

    def delete_by_id(self, _id: I):
        """Removes an entity by its id."""
        entity = self.get_by_id(_id)

        if not entity:
            default_logger.error(
                "Operation delete not permit on entity undefined")
            raise RepositoryIntegrityError(
                "Operation delete not permit on entity undefined")
        elif not entity.active:  # type: ignore
            default_logger.error("Entity %s, cannot be deleted", _id)
            raise RepositoryMissingElementError(
                str(_id), "cannot be deleted")  # type: ignore
        else:
            self.delete(entity)

    def delete_all(self):
        """Removes all entities."""
        query = self.create_builder().set_filter({'active': True}).build()
        for entity in query.all():
            entity.active = False

    def create_builder(self):
        """Create a new query builder instance"""
        return self.builder.set_session(self.session).set_model(self.entity)  # type: ignore

    def get_by_id(self, _id: I) -> E:
        """Get domain element by ID"""
        query = self.create_builder().build()
        return query.filter_by(id=_id).first()

    def get_by_id_lazy_select(self,  _id: I) -> E:
        """Get domain element by ID in mode lazy / select."""
        return self.session.get(self.entity, _id)  # type: ignore

    @abstractmethod
    def mapper_entity_to_dict(self, entity: E) -> dict:
        """Transform an entity to a dictionary."""

    def get_all(self) -> List[E]:
        """Retrieves all entities."""
        query = self.create_builder().build()
        return query.filter_by(active=True).all()

    def get_garbage_all(self) -> List[E]:
        """Retrieves all entities deleted that exist on garbage collector."""
        query = self.create_builder().build()
        return query.filter_by(active=False).all()

    def garbage_recover(self, entity: E):
        """Recover an entity from garbage collector."""
        if not entity.active:  # type: ignore
            entity.active = True  # type: ignore
            self.save(entity)
            self.session.flush()  # type: ignore
        else:
            default_logger.error("Entity %s, cant not be recovered", entity.id)
            raise RepositoryMissingElementError(
                str(entity.id), "cannot be recover")  # type: ignore

    def garbage_recover_by_id(self, _id: I):
        """Recover an entity from garbage collector by its id."""
        entity = self.get_by_id(_id)
        if entity:
            self.garbage_recover(entity)


class PagingAndSortingRepository(CrudRepository[I, E, S, B]):
    """PagingAndSortingRepository Class"""

    @abstractmethod
    def mapper_entity_to_dict(self, entity: E) -> dict:
        """Transform an entity to a dictionary."""

    def get_all(self, pageable: Optional[Pageable] = None) -> List[E]:
        """Retrieves pageable and sorted entities."""
        query = self.create_builder().set_options(pageable).build()
        return query.filter_by(active=True).all()


class JpaRepository(PagingAndSortingRepository[I, E, S, B]):
    """JpaRepository Class"""

    @abstractmethod
    def mapper_entity_to_dict(self, entity: E) -> dict:
        """Transform an entity to a dictionary."""

    def get_all(self, pageable: Optional[Pageable] = None, filters: Optional[dict] = None,
                group_by: Optional[list] = None, group_by_id: Optional[str] = None) -> List[E]:
        """
        Get all items: if defined retrieves each item list, pageable, sorted and groupped.

        :param pageable: Pageable object
        :param filters: Filters object
        :param group_by: Group by object
        :param group_by_id: Group by id object
        """
        query = self.create_builder().set_filter({'active': True}).set_filter(filters).set_group(
            group_by, group_by_id).set_options(pageable).build()

        return query.all()

    def save_and_flush(self, entity: E) -> E:
        """Save an entity and sync immediately."""
        try:
            self.save(entity)
            self.session.flush()  # type: ignore
            return entity
        except Exception as ex:  # pylint: disable=broad-except
            default_logger.exception("Error on save operation")
            raise RepositoryIntegrityError(
                "Error on save and flush operation") from ex

    def create(self, entity: E) -> E:
        """Create a new entity."""
        return self.save_and_flush(entity)

    def delete_all_in_batch(self):
        """Removes all entities in a single operation."""
        query = self.create_builder().set_filter({'active': True}).build()
        query.delete(synchronize_session=False)

    def delete_all_by_id_in_batch(self, ids):
        """Removes multiple entities by their ids in a single operation."""
        query = self.create_builder().set_filter({'active': True}).build()
        query.filter(self.entity.id.in_(ids)).delete(  # type: ignore
            synchronize_session=False)

    def find_by_spec(self, spec, pageable: Optional[Pageable] = None) -> List[E]:
        """Allows dynamic queries based on criteria."""
        query = self.create_builder().set_options(pageable).build()

        query = query.filter(*[getattr(self.entity, key) == value for key,
                             value in spec.items()]) if (isinstance(spec, dict)) else query.filter(spec)
        return query.all()
