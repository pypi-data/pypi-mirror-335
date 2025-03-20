"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from abc import ABC, abstractmethod
from typing import TypeVar, Protocol, Union, Generic

from pydantic import BaseModel

from nomenclators_archetype.infrastructure.http.schemas import SchemaSimpleNomenclatorResponse
from nomenclators_archetype.infrastructure.http.schemas import SchemaSimpleNomenclatorCreator
from nomenclators_archetype.infrastructure.http.schemas import SchemaSimpleNomenclatorUpdater

from nomenclators_archetype.infrastructure.http.schemas import SchemaNomenclatorResponse
from nomenclators_archetype.infrastructure.http.schemas import SchemaNomenclatorCreator
from nomenclators_archetype.infrastructure.http.schemas import SchemaNomenclatorUpdater

from nomenclators_archetype.domain.commons import BaseSimpleNomenclator, BaseNomenclator

D = TypeVar('D', bound=object)  # Domain class representation

# Schema response class representation
R_co = TypeVar('R_co', bound=BaseModel, covariant=True)  # type: ignore
# Schema creator class representation
C_contra = TypeVar('C_contra', bound=BaseModel, contravariant=True)
# Schema updater class representation
U_contra = TypeVar('U_contra', bound=BaseModel, contravariant=True)


class SchemaBaseMapper(Protocol[D, R_co, C_contra, U_contra]):
    """SchemaMapper class"""

    @staticmethod
    @abstractmethod
    def map_from_schema_to_domain(schema: Union[C_contra, U_contra]) -> D:
        """Map to Domain from Schema"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def map_from_domain_to_schema(domain: D) -> R_co:
        """Map to Schema from Domain"""
        raise NotImplementedError


class SchemaBaseNomenclatorMapper(ABC, Generic[D, R_co, C_contra, U_contra]):
    """Classe Nomenclator Mapper"""

    DomainClass: type
    SchemaResponseClass: type

    @classmethod
    @abstractmethod
    def map_from_schema_to_domain(cls, schema: Union[C_contra, U_contra]) -> D:
        """Map to Domain from Schema"""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def map_from_domain_to_schema(cls, domain: D) -> R_co:
        """Map to Schema from Domain"""
        raise NotImplementedError

    @classmethod
    def map_attributes(cls) -> dict:
        """Map bussines attributes vs schema attributes"""
        return {}


class SchemaSimpleNomenclatorMapper(SchemaBaseNomenclatorMapper, Generic[D, R_co, C_contra, U_contra]):
    """SchemaSimpleNomenclator Mapper class"""

    @classmethod
    def map_from_schema_to_domain(cls, schema: Union[C_contra, U_contra]) -> D:
        """Map to Domain from Schema"""
        if not cls.DomainClass:
            raise NotImplementedError(
                "The domain class (DomainClass) must be defined in the subclass")

        return cls.DomainClass(**schema.model_dump())

    @classmethod
    def map_from_domain_to_schema(cls, domain: D) -> R_co:
        """Map to Schema from Domain"""
        if not cls.SchemaResponseClass:
            raise NotImplementedError(
                "The persist class (SchemaClass) must be defined in the subclass")

        return cls.SchemaResponseClass(
            identifier=domain.id,  # type: ignore
            name=domain.name,  # type: ignore
            modified=domain.modified  # type: ignore
        )

    @classmethod
    def map_attributes(cls) -> dict:
        """Describe only mapping between bussines vs schema attributes"""

        return {
            "identifier": "id"
        }


class SchemaNomenclatorMapper(SchemaSimpleNomenclatorMapper, Generic[D, R_co, C_contra, U_contra]):
    """SchemaNomenclator Mapper class"""

    @classmethod
    def map_from_domain_to_schema(cls, domain: D) -> R_co:
        """Map to Schema from Domain"""
        if not cls.SchemaResponseClass:
            raise NotImplementedError(
                "The persist class (SchemaClass) must be defined in the subclass")

        return cls.SchemaResponseClass(
            identifier=domain.id,  # type: ignore
            name=domain.name,  # type: ignore
            description=domain.description,  # type: ignore
            modified=domain.modified  # type: ignore
        )


class MapperSchemaSimpleNomenclator(SchemaSimpleNomenclatorMapper
                                    [
                                        BaseSimpleNomenclator, SchemaSimpleNomenclatorResponse,
                                        SchemaSimpleNomenclatorCreator, SchemaSimpleNomenclatorUpdater
                                    ]
                                    ):
    """Mapper Schema Simple Nomenclator class"""
    DomainClass = BaseSimpleNomenclator
    SchemaResponseClass = SchemaSimpleNomenclatorResponse


class MapperSchemaNomenclator(SchemaNomenclatorMapper
                              [
                                  BaseNomenclator, SchemaNomenclatorResponse,
                                  SchemaNomenclatorCreator, SchemaNomenclatorUpdater
                              ]
                              ):
    """Mapper Schema Nomenclator class"""
    DomainClass = BaseNomenclator
    SchemaResponseClass = SchemaNomenclatorResponse
