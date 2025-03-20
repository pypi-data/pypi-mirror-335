"""
----------------------------------------------------------------------------------------------------
Written by Yovany Dominico Girón (y.dominico.giron@elprat.cat) for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from sqlalchemy import func

from nomenclators_archetype.domain.repository.builders import ASC_SORT_OPERATION, DESC_SORT_OPERATION
from nomenclators_archetype.domain.repository.builders import LOGICAL_OPERATIONS
from nomenclators_archetype.domain.repository.builders import COMPARISON_OPERATIONS
from nomenclators_archetype.domain.repository.builders import GT_OPERATION, GTE_OPERATION, LT_OPERATION, LTE_OPERATION, EQ_OPERATION, NEQ_OPERATION
from nomenclators_archetype.domain.repository.builders import LITERAL_OPERATIONS, LIKE_OPERATION, NOT_LIKE_OPERATION, IN_OPERATION, NOT_IN_OPERATION
from nomenclators_archetype.domain.repository.builders import QueryBuilder


class QueryBuilderImpl(QueryBuilder):
    """QueryBuilderImpl Class"""

    def apply_select_query(self):
        """Apply select query to infrastructure model"""
        super().apply_select_query()

        if self._selects:
            columns = [getattr(self._model, field, None)
                       for field in self._selects]
            if None in columns:
                raise ValueError("One or more fields are invalid.")

            query = self._session.query(*columns)  # type: ignore
        else:
            query = self._session.query(self._model)  # type: ignore

        return query

    def apply_filter_query(self, query):
        """Apply filter query to model SQLalchemyoperations"""
        query = super().apply_filter_query(query)

        for key, value in self._filters.items():
            column_name, operator = self.check_syntaxis_column_operator(key)

            if column_name is not None and column_name == "" and operator in LOGICAL_OPERATIONS:

                pass  # This issue will resolve on the future: for the momemnt will not implement the logical operations

            elif column_name is not None and operator in COMPARISON_OPERATIONS:

                column = getattr(self._model, column_name)
                if operator == EQ_OPERATION:
                    query = query.filter(column == value)
                elif operator == NEQ_OPERATION:
                    query = query.filter(column != value)
                elif operator == GT_OPERATION:
                    query = query.filter(column > value)
                elif operator == GTE_OPERATION:
                    query = query.filter(column >= value)
                elif operator == LT_OPERATION:
                    query = query.filter(column < value)
                elif operator == LTE_OPERATION:
                    query = query.filter(column <= value)

            elif column_name is not None and operator in LITERAL_OPERATIONS:

                column = getattr(self._model, column_name)
                if operator == LIKE_OPERATION:
                    query = query.filter(column.like(value))
                elif operator == NOT_LIKE_OPERATION:
                    query = query.filter(~column.like(value))
                elif operator == IN_OPERATION:
                    query = query.filter(column.in_(value))
                elif operator == NOT_IN_OPERATION:
                    query = query.filter(~column.in_(value))

            else:
                column = getattr(self._model, column_name)
                query = query.filter(column == value)

        return query

    def apply_group_query(self, query=None):
        """Apply group query to infrastructure model"""
        super().apply_group_query()

        group_columns = [getattr(self._model, field, None)
                         for field in self._grouping_by]
        if None in group_columns:
            raise ValueError("One or more model group fields are invalid.")

        if self._session is not None:

            if self._grouping_by_id_name is None:
                raise ValueError(
                    f"Identifier name should defined for {self._model.__name__ if self._model else 'Undefined class'}.")

            id_column = getattr(self._model, self._grouping_by_id_name, None)

            query = self._session.query(
                *group_columns,
                func.count(id_column).label(  # pylint: disable=not-callable
                    f"{self._model.__name__.lower() if self._model else 'id'}_count")
            ).group_by(*group_columns)
        elif query is None:
            raise ValueError(
                "Not exist previus query for grouping by operation.")
        else:
            query = query.group_by(*group_columns)

        return query

    def apply_pageable_query(self, query):
        """Apply pageable options query to infrastructure model"""
        super().apply_pageable_query(query)

        if self._pageable is not None and self._pageable.sort:
            for (sort_field_name, sort_orientation) in self._pageable.sort:

                if sort_field_name is None or sort_orientation is None or sort_orientation.upper() not in [ASC_SORT_OPERATION, DESC_SORT_OPERATION]:
                    raise ValueError(
                        f"Invalid sort tuple: {(sort_field_name, sort_orientation)}")

                persistence_class = self._model.__name__ if self._model else 'Undefined class'
                try:
                    column = getattr(self._model, sort_field_name, None)
                    if column is None:
                        raise ValueError(
                            f"For persistence class {persistence_class}, invalid column name: {sort_field_name}")

                    query = query.order_by(
                        column.desc() if sort_orientation.upper(
                        ) == DESC_SORT_OPERATION else column.asc()
                    )
                except AttributeError as e:
                    raise ValueError(
                        f"For persistence class {persistence_class}, error accessing attribute ' {sort_field_name}' ({e}).") from e

        if self._pageable is not None and self._pageable.pagination:
            query = query.limit(self._pageable.size).offset(
                (self._pageable.page) * self._pageable.size)

        return query
