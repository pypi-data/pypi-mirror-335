"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from datetime import datetime, date, time
from typing import Any, Optional, Dict, Union, Literal, List, Tuple

from pydantic import BaseModel, RootModel, Field

from nomenclators_archetype.domain.commons import NomenclatorId
from nomenclators_archetype.domain.repository.builders import COMPARISON_OPERATIONS, LITERAL_OPERATIONS


class SchemaPagination(BaseModel):
    """Schema Pagination class"""

    page: Optional[int] = Field(0,
                                ge=0, description="Número de página (en caso de utilizarse, debe ser >= 0)")
    element_for_page: Optional[int] = Field(10,
                                            gt=0, description="Elementos por página (en caso de utilizarse, debe ser > 0)")
    limit: Optional[int] = Field(None,
                                 gt=0, description="Máximo total de elementos a analizar (en caso de utilizarse, debe ser > 0)")
    element_sort: Optional[str] = Field(None,
                                        description="Campo por el cual se desea ordenar")
    sort: Optional[Literal["ASC", "DESC"]] = Field(
        "DESC", description="Orden 'ASC' para ordenar Ascendentemente o 'DESC' para ordenar Descendentemente")

    def sort_mapped(self) -> List[Tuple[str, str]]:
        """Get sorte mapped"""
        return [(self.element_sort, self.sort)] if self.element_sort else []


class SchemaFilterValue(BaseModel):
    """Schema FilterValue class: allows you to assign a direct value, a like/not like or a range"""

    eq: Optional[Union[str, int, float, datetime, date, time]] = Field(
        None, title="Igual a", description="Igual a", examples=["'eq': 'value'"])
    noteq: Optional[Union[str, int, float, datetime, date, time]] = Field(
        None, title="No igual a", description="No igual a", examples=["'noteq': 'value'"])
    like: Optional[str] = Field(None, title="Igual a (like)", description="Igual a (like)",
                                examples=["'like': 'value'"])
    notlike: Optional[str] = Field(None, title="No igual a (like)",
                                   description="No igual a (like)", examples=["'notlike': 'value'"])
    inc: Optional[list] = Field(None, title="Incluido en", description="Incluido en", examples=[
                                "'inc': ['value1', 'value2']"])
    notinc: Optional[list] = Field(None, title="No incluido en", description="No incluido en", examples=[
                                   "'notinc': ['value1', 'value2']"])
    gt: Optional[Union[int, float, datetime, date, time]] = Field(
        None, title="Mayor que", description="Mayor que", examples=["'gt': 1"])
    gte: Optional[Union[int, float, datetime, date, time]] = Field(
        None, title="Mayor o igual que", description="Mayor o igual que", examples=["'gte': 1"])
    lt: Optional[Union[int, float, datetime, date, time]] = Field(
        None, title="Menor que", description="Menor que", examples=["'lt': 1"])
    lte: Optional[Union[int, float, datetime, date, time]] = Field(
        None, title="Menor o igual que", description="Menor o igual que", examples=["'lte': 1"])


class SchemaFilters(RootModel[Dict[str, Union[SchemaFilterValue, list, str, int, float, datetime, date, time]]]):
    """Schema Filters class: allows you to assign a filter to a field"""

    def mapped(self, business_mapping: dict) -> Dict[str, Any]:
        """Get filters mapped"""

        filters = {}
        for key, value in self.root.items():

            if key in business_mapping:
                key = business_mapping[key]

            if isinstance(value, list):
                for item in list(value):
                    if isinstance(item, dict):
                        self._update_filter_value(filters, key, item)
                    elif isinstance(item, SchemaFilterValue):
                        self._update_filter_value(
                            filters, key, item.model_dump())
                    else:
                        raise ValueError(
                            f"Invalid filter value for key {key}: {item}")
            elif isinstance(value, SchemaFilterValue):
                self._update_filter_value(filters, key, value.model_dump())
            else:
                filters[key] = value

        return filters

    def _update_filter_value(self, filters: dict, key: str, value: dict) -> None:
        """Update schema filter value"""
        for sub_key, sub_value in value.items():
            if sub_value is not None:
                filters.update(self._map_filter(
                    key, sub_key, sub_value))

    def _map_filter(self, key: str, comparison_key: str, comparison_value: Any) -> dict:
        """
        Apply map filter to the key definition

        :param key: Key to filter
        :param comparison_key: comparing operator
        :param comparison_value: Value to comparison
        """
        if (
            (comparison_key.upper() in COMPARISON_OPERATIONS and isinstance(comparison_value, (str, int, float, datetime, date, time))) or
            (comparison_key.upper() in LITERAL_OPERATIONS and isinstance(
                comparison_value, (list, str)))
        ):
            return {f"{key}_{comparison_key.lower()}": comparison_value}
        else:
            return {}


class SchemaQueryParam(BaseModel):
    """Schema QueryParam class: allows you to assign a pagination and filter"""

    pagination: Optional[SchemaPagination] = Field(None, title="Paginación", description="Paginación", examples=[
                                                   {'page': 1, 'element_for_page': 10, 'limit': 100, 'element_sort': 'name', 'sort': 'ASC'}])

    filter: Optional[SchemaFilters] = Field(
        None, title="Filtros", description="Filtros", examples=[{'name': {'eq': 'value'}}])


class SchemaSimpleNomenclatorResponse(BaseModel):
    """Schema Simple Nomenclator Response class"""

    identifier: NomenclatorId = Field(..., title="Identificador",
                                      description="Identificador de un elemento en el nomenclador.")
    name: str = Field(..., min_length=1, title="Nombre",
                      description="Nombre de un elemento en el nomenclador.")
    modified: datetime = Field(..., title="Última actualización",
                               description="Fecha de la última actualización de un elemento en el nomenclador.")


class SchemaNomenclatorResponse(SchemaSimpleNomenclatorResponse):
    """Schema Nomenclator Response class"""

    description: Optional[str] = Field(None, min_length=1, title="Descripción",
                                       description="Descripción de un elemento en el nomenclador.")


class SchemaSimpleNomenclatorCreator(BaseModel):
    """Schema Simple Nomenclator Creator class"""

    name: str = Field(..., min_length=1, title="Nombre",
                      description="Nombre del elemento a crear en el nomenclador.")


class SchemaNomenclatorCreator(SchemaSimpleNomenclatorCreator):
    """Schema Nomenclator Creator class"""

    description: Optional[str] = Field(None, min_length=1, title="Descripción",
                                       description="Descripción del elemento a crear en el nomenclador.")


class SchemaSimpleNomenclatorUpdater(BaseModel):
    """Schema Simple Nomenclator Updater class"""

    identifier: NomenclatorId = Field(..., title="Identificador",
                                      description="Identificador de un elemento en el nomenclador.")
    name: str = Field(..., min_length=1, title="Nombre",
                      description="Nombre del elemento a crear en el nomenclador.")


class SchemaNomenclatorUpdater(SchemaSimpleNomenclatorUpdater):
    """Schema Nomenclator Updater class"""

    description: Optional[str] = Field(None, min_length=1, title="Descripción",
                                       description="Descripción del elemento a crear en el nomenclador.")
