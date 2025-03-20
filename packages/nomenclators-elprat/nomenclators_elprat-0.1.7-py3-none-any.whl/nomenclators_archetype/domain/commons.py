"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from abc import ABC
from typing import Union, Optional
from datetime import datetime

NomenclatorId = Union[int, str, None]


class BaseSimpleNomenclator(ABC):
    """Classe base para los nomencladores"""

    def __init__(self, name: str, identifier: Optional[NomenclatorId] = None, updated_at: Optional[datetime] = None):
        if not name:
            raise ValueError(
                "The 'name' field of the nomenclator is mandatory")

        self.id = identifier
        self.name = name
        self._updated_at = updated_at

    def __composite_values__(self) -> tuple:
        return (
            self.id, self.name, self._updated_at
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(\n"
            f"  id={self.id}, name={self.name}, updated={self._updated_at} \n"
            f")"
        )

    def __str__(self):
        return f"{self.__class__.__name__}: '{self.name}'"

    def __eq__(self, other):
        if not isinstance(other, BaseSimpleNomenclator):
            return False

        return (self.id == other.id and self.name == other.name)

    def __hash__(self):
        return hash((self.id, self.name))

    @property
    def modified(self) -> Optional[datetime]:
        """Return the last modification date of the nomenclator."""
        return self._updated_at


class BaseNomenclator(BaseSimpleNomenclator):
    """Classe base para los nomencladores con descripción"""

    def __init__(self, name: str, description: Optional[str] = None,
                 identifier: Optional[NomenclatorId] = None,
                 updated_at: Optional[datetime] = None
                 ):
        super().__init__(name, identifier=identifier, updated_at=updated_at)

        if not description:
            raise ValueError(
                "The 'description' field of the nomenclator is mandatory")

        self.description = description

    def __composite_values__(self) -> tuple:
        return (
            self.id, self.name, self.description
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(\n"
            f"  id={self.id}, name={self.name}, \n"
            f"  description={self.description}, \n"
            f"  updated={self._updated_at} \n"
            f")"
        )


class TreeNomenclator(ABC):
    """Classe base para los nomencladores jerárquicos."""

    def __init__(self, identifier: Optional[NomenclatorId] = None,
                 name: Optional[str] = None, parent: Optional[NomenclatorId] = None,
                 level: Optional[int] = None, path: Optional[str] = None):

        self.id = identifier
        self.name = name
        self.parent = parent
        self.level = level
        self.path = path

    def __composite_values__(self) -> tuple:
        return (
            self.id, self.name, self.parent, self.level, self.path
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(\n"
            f"  id={self.id}, name={self.name}, \n"
            f"  parent={self.parent}, level={self.level}, \n"
            f"  path={self.path} \n"
            f")"
        )
