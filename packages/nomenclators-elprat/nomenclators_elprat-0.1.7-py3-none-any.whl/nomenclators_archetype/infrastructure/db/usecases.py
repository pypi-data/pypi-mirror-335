"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
import traceback
from abc import ABC

from typing import Generic, TypeVar, Optional

from sqlalchemy.orm import Session

from nomenclators_archetype.domain.loggers import default_logger

from nomenclators_archetype.domain.usecase.commons import decorator_use_case_validator
from nomenclators_archetype.domain.usecase.commons import UseCaseIsolatedSession
from nomenclators_archetype.domain.usecase.commons import UseCaseSharedSession
from nomenclators_archetype.domain.usecase.commons import ValidatorUseCaseIsolatedSession
from nomenclators_archetype.domain.usecase.commons import ValidatorUseCaseSharedSession

I = TypeVar('I', bound=object)  # Intentifier class representation
D = TypeVar('D', bound=object)  # Domian class representation
S = TypeVar('S', bound=object)  # Service class representation


class BaseUnitOfWork(ABC):
    """Base UnitOfWork class for database transactions"""

    def __init__(self):  # type: ignore
        self.session = None

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Close the session and manager commit or rollback transaction

        :param exc_type: Exception type if occurs an exception
        :param exc_value: Exception value
        :param exc_traceback: Traceback of the exception
        """

        if exc_type is None:
            self.session.commit()  # type: ignore
        else:
            error_message = "".join(traceback.format_exception(
                exc_type, exc_value, exc_traceback))
            self.session.rollback()  # type: ignore
            default_logger.error("Errores detectados:\n %s", error_message)
            raise exc_value

        self.session.close()  # type: ignore

    def commit(self):
        """Force the commit over the transaction"""
        if self.session:
            self.session.commit()  # type: ignore

    def rollback(self):
        """Force the rollback over the transaction"""
        if self.session:
            self.session.rollback()  # type: ignore


class UnitOfWorkIsolatedSession(BaseUnitOfWork):
    """UnitOfWork class for database transactions with isolated session"""

    def __init__(self, session_factory: callable):  # type: ignore
        super().__init__()
        self._session_factory = session_factory

    def __enter__(self):
        self.session = self._session_factory()
        return self


class UnitOfWorkSharedSession(BaseUnitOfWork):
    """UnitOfWork class for database transactions with shared session"""

    def __init__(self, db_session: Session):  # type: ignore
        super().__init__()
        self.session = db_session

    def __enter__(self):
        return self


class DefaultUseCaseNomenclatorCreatorIsolatedSession(ValidatorUseCaseIsolatedSession, Generic[D, S]):
    """Default Use Case Nomenclator creator with isolated session class"""

    @decorator_use_case_validator
    def invoke(self, data: D) -> Optional[D]:  # pylint: disable=arguments-differ # type: ignore
        """Invoke the use case"""
        with UnitOfWorkIsolatedSession(self._session_factory) as uow:
            self.service.set_session(uow.session)
            return self.service.create_item(data)


class DefaultUseCaseNomenclatorCreatorSharedSession(UseCaseSharedSession, Generic[D, S]):
    """Default Use Case Nomenclator creator with shared session class"""

    def invoke(self, data: D) -> Optional[D]:  # pylint: disable=arguments-differ # type: ignore
        """Invoke the use case"""
        with UnitOfWorkSharedSession(self.session):
            return self.service.create_item(data)


class DefaultUseCaseNomenclatorUpdaterIsolatedSession(ValidatorUseCaseIsolatedSession, Generic[D, S]):
    """Default Use Case Nomenclator updater with isolated session class"""

    def integrity_validator(self, *params, **kparams) -> list:
        """Method to validate the use case integrity"""
        return ([{"param": "id", "message": "Not match with item identifier"}]
                if len(params) == 2 and str(params[0].id) != params[1] else [])

    @decorator_use_case_validator
    def invoke(self, data: D, _id: Optional[I] = None) -> Optional[D]:  # pylint: disable=arguments-differ # type: ignore
        """Invoke the use case"""
        with UnitOfWorkIsolatedSession(self._session_factory) as uow:
            self.service.set_session(uow.session)
            return self.service.update_item(data)


class DefaultUseCaseNomenclatorUpdaterSharedSession(ValidatorUseCaseSharedSession, Generic[D, S]):
    """Default Use Case Nomenclator updater with shared session class"""

    def integrity_validator(self, *params, **kparams) -> list:
        """Method to validate the use case integrity"""
        return ([{"param": "id", "message": "Not match with item identifier"}]
                if len(params) == 2 and str(params[0].id) != params[1] else [])

    @decorator_use_case_validator
    def invoke(self, data: D, _id: Optional[I] = None) -> Optional[D]:  # pylint: disable=arguments-differ # type: ignore
        """Invoke the use case"""
        with UnitOfWorkSharedSession(self.session):
            return self.service.update_item(data)


class DefaultUseCaseNomenclatorDeleterIsolatedSession(UseCaseIsolatedSession, Generic[I, D, S]):
    """Default Use Case Nomenclator deleter with isolated session class"""

    def invoke(self, _id: I) -> Optional[D]:  # pylint: disable=arguments-differ # type: ignore
        """Invoke the use case"""
        with UnitOfWorkIsolatedSession(self._session_factory) as uow:
            self.service.set_session(uow.session)
            return self.service.delete_by_id(_id)


class DefaultUseCaseNomenclatorDeleterSharedSession(UseCaseSharedSession[I, D, S]):
    """Default Use Case Nomenclator deleter with shared session class"""

    def invoke(self, _id: I) -> Optional[D]:  # pylint: disable=arguments-differ # type: ignore
        """Invoke the use case"""
        with UnitOfWorkSharedSession(self.session):
            return self.service.delete_by_id(_id)
