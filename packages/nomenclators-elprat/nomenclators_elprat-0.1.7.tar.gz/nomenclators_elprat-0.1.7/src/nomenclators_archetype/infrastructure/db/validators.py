"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from typing import TypeVar, Protocol, Optional, Union

from nomenclators_archetype.domain.commons import NomenclatorId
from nomenclators_archetype.domain.commons import BaseSimpleNomenclator

from nomenclators_archetype.domain.validator.commons import BaseValidator

I = TypeVar('I', bound=NomenclatorId)  # Identifier class representation
S = TypeVar('S', bound=BaseSimpleNomenclator)  # Service class representation


class EntityValidator(BaseValidator, Protocol[I, S]):
    """EntityValidator class"""

    @classmethod
    def validate_foreign_key(cls, identifier: I, service: S) -> Optional[Union[str, dict]]:
        """Validate the foreign key"""
        item = service.get_item_by_id(identifier)
        return {'reference': identifier, 'message': f"no se encuentra en la entidad {service.__class__}."} if item is None else None

    @classmethod
    def validate_unique_element(cls, service: S, spec: dict) -> Optional[Union[str, dict]]:
        """Validate the unique element"""

        items = service.find_by_spec(spec)
        return {"reference": ', '.join(spec.keys()), "message": f"se encuentran en la entidad {service.__class__} con los valores [{', '.join(str(value) for value in spec.values())}]."} if len(items) > 0 else None

    @classmethod
    def validate_unique_updatable_element(cls, service: S, origin_spec: dict, target_spec: Optional[dict] = None) -> Optional[Union[str, dict]]:
        """Validate the updatable element"""

        origin_items = service.find_by_spec(origin_spec)
        if len(origin_items) == 0:
            return {"reference": ', '.join(origin_spec.keys()), "message": f"no se encuentran registro en la entidad {service.__class__} con los valores [{', '.join(str(value) for value in origin_spec.values())}] para poderlo actualizar."}

        if target_spec is not None:
            target_items = service.find_by_spec(target_spec)
            return {"reference": ', '.join(origin_spec.keys()), "message": f"se encuentran en la entidad {service.__class__} con los valores [{', '.join(str(value) for value in origin_spec.values())}]."} if len(target_items) > 0 else None
        else:
            return {"reference": ', '.join(origin_spec.keys()), "message": f"se encuentran más de un registro en la entidad {service.__class__} con los valores [{', '.join(str(value) for value in origin_spec.values())}] para saber a quien actualizar."} if len(origin_items) > 1 else None
