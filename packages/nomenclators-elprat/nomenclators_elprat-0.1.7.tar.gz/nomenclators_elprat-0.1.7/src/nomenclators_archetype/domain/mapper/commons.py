"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from abc import ABC, abstractmethod
from typing import TypeVar, Protocol, Dict

D = TypeVar('D', bound=object)  # Domain class representation
P = TypeVar('P', bound=object)  # Persistence class representation


class ModelMapper(Protocol[D, P]):
    """ModelMapper class"""

    _attr_map: Dict[str, str]

    def map_attr(self, attr: str):
        """Map attribute domain name to attribute persistence name"""
        return attr if not hasattr(self, '_attr_map') else mapped_attr_dict(_attr=attr, _dict=self._attr_map)

    @staticmethod
    @abstractmethod
    def map_from_entity_to_domain(persistence: P) -> D:
        """Map to Domain from Persistence Entity"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def map_from_domain_to_entity(domain: D) -> P:
        """Map to Persistence Entity from Domain"""
        raise NotImplementedError


class NomenclatorMapper(ABC):
    """Nomenclator Mapper class"""

    DomainClass: type
    PersistenceClass: type

    _attr_map: Dict[str, str]

    @classmethod
    def map_attr(cls, attr: str):
        """Map attribute domain name to attribute persistence name"""
        return attr if not hasattr(cls, '_attr_map') else mapped_attr_dict(_attr=attr, _dict=cls._attr_map)

    @classmethod
    @abstractmethod
    def map_from_entity_to_domain(cls, persistence):
        """Map to Domain from Persistence Entity"""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def map_from_domain_to_entity(cls, domain):
        """Map to Persistence Entity from Domain"""
        raise NotImplementedError


class BaseSimpleNomenclatorMapper(NomenclatorMapper):
    """BaseSimpleNomenclator Mapper class"""

    @classmethod
    def map_from_entity_to_domain(cls, persistence):
        """Map to Domain from Persistence Entity"""

        if not cls.DomainClass:
            raise NotImplementedError(
                "The domain class (DomainClass) must be defined in the subclass")

        if persistence is not None:
            return cls.DomainClass(
                identifier=persistence.id,
                name=persistence.name,
                updated_at=persistence.updated_at
            )
        else:
            return None

    @classmethod
    def map_from_domain_to_entity(cls, domain):
        """Map to Persistence Entity from Domain"""

        if not cls.PersistenceClass:
            raise NotImplementedError(
                "The persist class (PersistenceClass) must be defined in the subclass")

        if domain is not None:
            return cls.PersistenceClass(
                id=domain.id,
                name=domain.name
            )
        else:
            return None


class BaseNomenclatorMapper(NomenclatorMapper):
    """BaseNomenclator Mapper Class"""

    @classmethod
    def map_from_entity_to_domain(cls, persistence):
        """Map to Domain from Persistence Entity"""

        if not cls.DomainClass:
            raise NotImplementedError(
                "The domain class (DomainClass) must be defined in the subclass")

        if persistence is not None:
            return cls.DomainClass(
                identifier=persistence.id,
                name=persistence.name,
                description=persistence.description,
                updated_at=persistence.updated_at
            )
        else:
            return None

    @classmethod
    def map_from_domain_to_entity(cls, domain):
        """Map to Persistence Entity from Domain"""

        if not cls.PersistenceClass:
            raise NotImplementedError(
                "The persist class (PersistenceClass) must be defined in the subclass")

        if domain is not None:
            return cls.PersistenceClass(
                id=domain.id,
                name=domain.name,
                description=domain.description
            )
        else:
            return None


class TreeNomenclatorMapper(NomenclatorMapper):
    """TreeNomenclator Mapper Class"""

    @classmethod
    def map_from_entity_to_domain(cls, persistence):
        """Map to Domain from Persistence Entity"""

        if not cls.DomainClass:
            raise NotImplementedError(
                "The domain class (DomainClass) must be defined in the subclass")

        if persistence is not None:
            return cls.DomainClass(
                identifier=persistence.id,
                name=persistence.name,
                parent=persistence.parent,
                level=persistence.level,
                path=persistence.path
            )
        else:
            return None

    @classmethod
    def map_from_domain_to_entity(cls, domain):
        """Map to Persistence Entity from Domain"""

        if not cls.PersistenceClass:
            raise NotImplementedError(
                "The persist class (PersistenceClass) must be defined in the subclass")

        if domain is not None:
            return cls.PersistenceClass(
                id=domain.id,
                name=domain.name,
                parent=domain.parent,
                level=domain.level,
                path=domain.path
            )
        else:
            return None


def mapped_attr_dict(_attr: str, _dict: Dict[str, str]):
    """
    Get the mapped attribute of a dictionary

    Args:
        _attr: Attribute name to find on the dictionary
        _dict: dictionary with the mapping

    Returns:
        Resulting mapped attribute if found, otherwise the original attribute name
    """
    attr_mapped = _dict.get(_attr)
    if attr_mapped is None:
        attr_mapped = _attr

    return attr_mapped
