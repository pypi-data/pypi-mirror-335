"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from typing import Protocol, Optional, Union


class BaseValidator(Protocol):
    """BaseValidator class"""

    @classmethod
    def validate_invoke_params(cls, *params) -> Optional[Union[str, dict]]:
        """Validate the parameters to invoke the use case"""
        return {'param': 'id', 'message': 'Not match with item identifier'} if len(params) == 2 and str(params[0].id) != params[1] else None
