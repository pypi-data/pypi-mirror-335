"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from typing import Union


class InvalidEventTypeException(Exception):
    """Raised when the event does not valid type."""

    def __init__(self):
        super().__init__("Event with invalid type")


class InvalidParameterTypeException(Exception):
    """Raised when the parameter does not valid type."""

    def __init__(self):
        super().__init__("Invalid Parameter type")


class EmptyContextException(Exception):
    """Raised when the context is empty."""

    def __init__(self):
        super().__init__("Empty context")


class ParameterCountException(Exception):
    """Raised when has too many parameter."""

    def __init__(self):
        super().__init__("Too many parameter")


class RequiredParameterException(Exception):
    """Raised when the require parameter on Class"""

    def __init__(self, cls_name):
        super().__init__(f"`{cls_name}` had parameter required")


class RequiredElementError(Exception):
    """Raised when the require element on Class"""

    def __init__(self, cls_name):
        super().__init__(f"`{cls_name}`, had required")


class BusinessIntegrityError(Exception):
    """Raised when the domain integrity error on Class"""

    def __init__(self, cls_name, errors: list[Union[str, dict]]):
        if not isinstance(errors, list):
            raise ValueError("Errors must be a list")

        self.errors = errors
        self._cls_name = cls_name
        super().__init__()

    def __composite_values__(self) -> tuple:
        return (
            self.errors
        )

    def __repr__(self):
        return (
            f"{self._cls_name}"
            f"(\n"
            f"  errors={self.errors} \n"
            f")"
        )

    def __str__(self):
        return f"`{self._cls_name}`" + ((', had integrity business exception problems:\n' + self._format_errors()) if self.errors else ' integrity business exception.')

    def _format_errors(self):
        return '\n'.join([str(error) for error in self.errors]) if self.errors else ''
