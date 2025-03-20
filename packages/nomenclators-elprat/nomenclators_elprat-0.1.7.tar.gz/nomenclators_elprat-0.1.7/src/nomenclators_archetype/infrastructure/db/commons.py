"""
----------------------------------------------------------------------------------------------------
Written by: 
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)
  
for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from typing import Any, Optional

from sqlalchemy import func
from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy.orm import mapped_column, as_declarative, Session
from sqlalchemy.inspection import inspect
from sqlalchemy.ext.declarative import declared_attr


@as_declarative()
class Base:
    """Classe base para los modelos de la base de datos."""

    id: Any
    __name__: str

    @declared_attr  # type: ignore
    def __tablename__(self) -> str:
        return self.__name__.lower()

    @classmethod
    def contains_item_on_string(cls, node: str, elements: list[str]):
        """Determina si el nodo contiene al menos una de las palabras de la lista de elementos."""

        for word in elements:
            if word in node:
                return True

        return False


class BaseSimpleNomenclator(Base):
    """Classe base para los nomencladores simples."""

    __abstract__ = True

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(64), unique=True)

    active = mapped_column(Boolean, default=True)

    created_at = mapped_column(
        DateTime, server_default=func.now(), nullable=False)  # pylint: disable=not-callable

    updated_at = mapped_column(
        DateTime, server_default=func.now(), nullable=False, onupdate=func.now())  # pylint: disable=not-callable

    def __str__(self) -> str:
        return f"({self.id}, {self.name})"

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name }:(id={self.id}, name={self.name})"


class BaseNomenclator(BaseSimpleNomenclator):
    """Classe base para los nomencladores."""

    __abstract__ = True

    description = mapped_column(String(255), nullable=False)

    def __str__(self) -> str:
        return f"({self.id}, {self.name}, {self.description})"

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name }:(id={self.id}, name={self.name}, description={self.description})"


def entity2dict(entity, ignored_fields: Optional[list[str]] = None) -> dict:
    """Transform an entity item to a dictionary."""
    state = inspect(entity)
    return {
        attr.key: getattr(entity, attr.key) for attr in
        state.attrs if attr.key != '_sa_instance_state' and  # type: ignore
        (ignored_fields is None or attr.key not in ignored_fields)
    }


class TreeNomenclator(BaseSimpleNomenclator):
    """Classe base para los nomencladores jerárquicos."""

    __abstract__ = True

    parent = mapped_column(Integer)
    level = mapped_column(Integer)
    path = mapped_column(String(255))

    def __str__(self) -> str:
        return f"({self.id}, {self.name}, {self.parent}, {self.level}, {self.path})"

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name }:(id={self.id}, name={self.name}, parent={self.parent}, level={self.level}, path={self.path})"


def update_tree_path(mapper, connection, target):  # pylint: disable=unused-argument
    """
    Actualiza el campo 'path' del nodo basado en la secuencia de campos 'name' de sus padres en cascada.

    :param mapper: Mapper de la clase.
    :param connection: Conexión de la base de datos.
    :param target: Nodo a actualizar
    """
    session = Session.object_session(target)
    if not session:
        return

    path_parts = [target.name]
    parent = target.parent
    level = 0

    while parent:
        parent_node = session.get(target.__class__, parent)
        if parent_node:
            path_parts.append(parent_node.name)
            parent = parent_node.parent
            level += 1
        else:
            break

    target.path = " > ".join(reversed(path_parts))
    target.level = level
