"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from abc import abstractmethod
from typing import Union, Optional, List, Tuple

from nomenclators_archetype.domain.exceptions import RequiredElementError

OR_OPERATION = "OR"
AND_OPERATION = "AND"

LOGICAL_OPERATIONS = [OR_OPERATION, AND_OPERATION]

GT_OPERATION = "GT"
GTE_OPERATION = "GTE"
LT_OPERATION = "LT"
LTE_OPERATION = "LTE"
EQ_OPERATION = "EQ"
NEQ_OPERATION = "NOTEQ"

COMPARISON_OPERATIONS = [GT_OPERATION, GTE_OPERATION, LT_OPERATION,
                         LTE_OPERATION, EQ_OPERATION, NEQ_OPERATION]

LIKE_OPERATION = "LIKE"
NOT_LIKE_OPERATION = "NOTLIKE"
IN_OPERATION = "INC"
NOT_IN_OPERATION = "NOTINC"

LITERAL_OPERATIONS = [LIKE_OPERATION,
                      NOT_LIKE_OPERATION, IN_OPERATION, NOT_IN_OPERATION]

RESERVED_OPERATIONS = LOGICAL_OPERATIONS + \
    COMPARISON_OPERATIONS + LITERAL_OPERATIONS

ASC_SORT_OPERATION = "ASC"
DESC_SORT_OPERATION = "DESC"


class Pageable:
    """Pageable Class"""

    def __init__(self, page: int = 0, size: int = 10, limit: Optional[int] = None,
                 pagination: bool = False, sort: Optional[List[Tuple[str, str]]] = None):

        if sort is None:
            sort = []

        self.page = page
        self.size = size
        self.limit = limit
        self.pagination = pagination
        self.sort = sort


class QueryBuilder():
    """QueryBuilder Class"""

    def __init__(self):
        self._model = None
        self._session = None
        self._selects = []
        self._filters = {}
        self._grouping_by = []
        self._grouping_by_id_name = None
        self._pageable = None

    def set_select(self, *_fields):
        """Defines the columns to select"""
        self._selects = self._selects.extend(_fields)  # type: ignore
        return self

    def set_filter(self, _fields_filters):
        """Define the pairs comparations filters"""
        if _fields_filters:
            self._filters = self.__apply_filter_operations_deep_update(
                self._filters, _fields_filters)
        return self

    def set_group(self, _fields__grouping_by, _fields__grouping_by_id: str = "id"):
        """
        Defines the group columns to select

        :param _fields__grouping_by: List of columns to group by
        :param _fields__grouping_by_id: Column to group by id
        """
        if _fields__grouping_by and _fields__grouping_by_id:
            self._selects = []
            self._grouping_by = _fields__grouping_by
            self._grouping_by_id_name = _fields__grouping_by_id
        return self

    def set_options(self, pageable: Pageable):
        """Define paginable options"""
        self._pageable = pageable
        return self

    def set_model(self, model):
        """Define the model to query"""
        self._model = model
        self._filters = {}
        return self

    def set_session(self, session):
        """Define the session to query"""
        self._session = session
        return self

    def initializate(self):
        """Initializate the query builder"""
        self._model = None
        self._session = None
        self._selects = []
        self._filters = {}
        self._grouping_by = []
        self._grouping_by_id_name = None
        self._pageable = None
        return self

    def build(self):
        """Build the query"""

        if self._session is None:
            raise RequiredElementError(
                "The database session for queries builder is not defined")

        if self._model is None:
            raise RequiredElementError(
                "The entity model for queries builder is not defined")

        if self._grouping_by:
            query = self.apply_group_query()
        else:
            query = self.apply_select_query()

        if self._filters:
            query = self.apply_filter_query(query)

        if self._grouping_by:
            query = self.apply_group_query(query)

        if self._pageable:
            query = self.apply_pageable_query(query)

        return query

    def __apply_filter_operations_deep_update(self, _original_filters, _new_filters):
        """
        Apply filter operations deep update

        :param _original_filters: Filters previously existing
        :param _new_filters: New filters to apply
        """

        for key, value in _new_filters.items():
            if (key == OR_OPERATION or key == AND_OPERATION) and not isinstance(value, dict):
                raise RequiredElementError(
                    f"The operation {key} should be a dictionary with filters")

            if (key == OR_OPERATION or key == AND_OPERATION) and key in _original_filters:
                self.__apply_filter_operations_deep_update(
                    _original_filters[key], value)
            else:
                _original_filters[key] = value

        return _original_filters

    def check_syntaxis_column_operator(self, key) -> tuple[str, Union[str, None]]:
        """Apply operator to filter query"""
        try:
            column_name, operator = key.split("_")

            if operator is None or operator.upper() not in RESERVED_OPERATIONS:
                return key, None
            else:
                return column_name, operator.upper()
        except ValueError:
            return key, None

    @abstractmethod
    def apply_select_query(self):
        """Apply select query to infrastructure model"""

        if self._session is None:
            raise RequiredElementError(
                "The database session for queries builder is not defined")

        if self._model is None:
            raise RequiredElementError(
                "The entity model for queries builder is not defined")

    @abstractmethod
    def apply_filter_query(self, query):
        """Apply filter query to infrastructure model"""

        if not self._filters:
            raise RequiredElementError(
                "The filter's for queries builder is not defined")

        if self._model is None:
            raise RequiredElementError(
                "The entity model for queries builder is not defined")

        return query

    @abstractmethod
    def apply_group_query(self, query: Optional[object] = None):
        """Apply group query to infrastructure model"""

        if self._model is None:
            raise RequiredElementError(
                "The entity model for queries builder is not defined")

        if self._grouping_by is None:
            raise RequiredElementError(
                "The group definition for queries builder is not defined")

    @abstractmethod
    def apply_pageable_query(self, query):
        """Apply pageable options query to infrastructure model"""

        if self._model is None:
            raise RequiredElementError(
                "The entity model for queries builder is not defined")

        if self._pageable is None:
            raise RequiredElementError(
                "The pagable options for queries builder is not defined")
