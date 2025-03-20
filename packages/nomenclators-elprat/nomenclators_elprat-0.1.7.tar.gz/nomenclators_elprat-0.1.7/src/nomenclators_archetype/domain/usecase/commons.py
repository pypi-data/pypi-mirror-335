"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, TypeVarTuple, Optional, Union

from nomenclators_archetype.domain.loggers import default_logger
from nomenclators_archetype.domain.exceptions import RequiredElementError, BusinessIntegrityError

R = TypeVar('R', bound=object)  # Response class representation

P = TypeVarTuple('P')  # Property class representation


class BaseUseCase(ABC, Generic[R, *P]):
    """Base class for use cases"""

    def __init__(self, services: Optional[Union[object, dict[str, object]]] = None):
        if isinstance(services, dict):
            self.__dict__[
                "_services"] = services if services is not None else {}
        elif services is not None:
            self.__dict__["_services"] = {"service": services}

    def __getattr__(self, property_name) -> P:  # type: ignore

        if property_name in self.__dict__:
            return self.__dict__[property_name]

        services = self.__dict__.get("_services", {})
        if property_name in services:
            return services[property_name]  # type: ignore
        raise RequiredElementError(
            f"The service / property '{property_name}', isn't defined")

    def __dir__(self):
        base_attrs = list(super().__dir__())
        instance_attrs = list(self.__dict__.keys())
        services_attrs = list(self.__dict__.get("_services", {}).keys())
        return sorted(set(base_attrs + instance_attrs + services_attrs))

    @abstractmethod
    def invoke(self, *params, **kparams) -> R:
        """Invoke the use case"""
        raise NotImplementedError

    def _set_session(self, session, services: Optional[Union[object, dict[str, object]]] = None):
        """Set the session to all services"""
        if isinstance(services, dict):
            for service in services.values():
                service.set_session(session)
        else:
            services.set_session(session)


def decorator_use_case_validator(invoke_method):
    """Decorator to validate the use case before invoke"""

    def wrapper(self, *args, **kwargs):
        errors = self.before_invoke(self, *args, **kwargs)
        if errors:
            default_logger.error("Errores detectados:\n %s", errors)
            raise BusinessIntegrityError(self.__class__.__name__, errors)
        return invoke_method(self, *args, **kwargs)
    return wrapper


class ValidatorUseCase(BaseUseCase, Generic[R, *P]):
    """Use Case validation class"""

    def before_invoke(self, *params, **kparams) -> list:
        """Method to validate the use case before invoke"""
        error = self.integrity_validator(*params, **kparams)
        if error:
            return error
        return self.business_validator(*params, **kparams)

    def integrity_validator(self, *params, **kparams) -> list:  # pylint: disable=unused-argument
        """Method to validate the use case integrity"""
        return []

    def business_validator(self, *params, **kparams) -> list:  # pylint: disable=unused-argument
        """Method to validate the use case business rules"""
        return []

    @abstractmethod
    @decorator_use_case_validator
    def invoke(self, *params, **kparams) -> R:
        """Invoke the use case"""
        raise NotImplementedError


class UseCaseIsolatedSession(BaseUseCase, Generic[R, *P]):
    """Use Case isolated session class"""

    def __init__(self, session_factory, services: Optional[Union[object, dict[str, object]]] = None):
        self._session_factory = session_factory
        super().__init__(services=services)


class UseCaseSharedSession(BaseUseCase, Generic[R, *P]):
    """Use Case with shared session class"""

    def __init__(self, db_session, services: Optional[Union[object, dict[str, object]]] = None):
        self.session = db_session
        self._set_session(db_session, services)
        super().__init__(services=services)


class ValidatorUseCaseIsolatedSession(ValidatorUseCase, Generic[R, *P]):
    """Use Case validator isolated session class"""

    def __init__(self, session_factory, services: Optional[Union[object, dict[str, object]]] = None):
        self._session_factory = session_factory
        super().__init__(services=services)


class ValidatorUseCaseSharedSession(ValidatorUseCase, Generic[R, *P]):
    """Use Case validator with shared session class"""

    def __init__(self, db_session, services: Optional[Union[object, dict[str, object]]] = None):
        self.session = db_session
        self._set_session(db_session, services)
        super().__init__(services=services)
