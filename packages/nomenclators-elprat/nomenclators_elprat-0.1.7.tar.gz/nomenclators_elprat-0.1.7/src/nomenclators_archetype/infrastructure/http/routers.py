"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón (y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
from typing import TypeVar, List, Generic, Type, Optional

from fastapi import APIRouter, Request, Response, Body, status
from fastapi.responses import JSONResponse

from nomenclators_archetype.domain.commons import NomenclatorId
from nomenclators_archetype.domain.exceptions import RequiredElementError, BusinessIntegrityError

from nomenclators_archetype.domain.repository.builders import Pageable
from nomenclators_archetype.domain.repository.commons import RepositoryIntegrityError, RepositoryMissingElementError

from nomenclators_archetype.domain.service.commons import NomenclatorService
from nomenclators_archetype.domain.usecase.commons import BaseUseCase

from nomenclators_archetype.infrastructure.http.mappers import SchemaBaseNomenclatorMapper
from nomenclators_archetype.infrastructure.http.mappers import MapperSchemaSimpleNomenclator
from nomenclators_archetype.infrastructure.http.mappers import MapperSchemaNomenclator

from nomenclators_archetype.infrastructure.http.schemas import SchemaQueryParam
from nomenclators_archetype.infrastructure.http.schemas import SchemaSimpleNomenclatorResponse
from nomenclators_archetype.infrastructure.http.schemas import SchemaSimpleNomenclatorCreator, SchemaSimpleNomenclatorUpdater

from nomenclators_archetype.infrastructure.http.schemas import SchemaNomenclatorResponse
from nomenclators_archetype.infrastructure.http.schemas import SchemaNomenclatorCreator, SchemaNomenclatorUpdater

from nomenclators_archetype.infrastructure.http.exceptions import ForbiddenException, NotFoundException, ConflictException
from nomenclators_archetype.infrastructure.http.exceptions import UnprocessableEntityException

# Mapper class representation
M = TypeVar('M', bound=SchemaBaseNomenclatorMapper)

# Response class representation
R = TypeVar('R', bound=SchemaSimpleNomenclatorResponse)

# Creator class representation
C = TypeVar('C', bound=SchemaSimpleNomenclatorCreator)

# Updater class representation
U = TypeVar('U', bound=SchemaSimpleNomenclatorUpdater)


class BaseNomenclatorRouter(APIRouter, Generic[M]):
    """Base Nomenclator Router class"""

    def __init__(self, *args,
                 service: NomenclatorService, mapper: Type[M],
                 creator_uc: BaseUseCase, updater_uc: BaseUseCase, deleter_uc: BaseUseCase,
                 default_name: str = "Default", **kwargs):
        """Constructor for BaseNomenclatorRouter class"""

        if service is None:
            raise RequiredElementError(
                "Service is required: The service for router is not defined")
        if mapper is None:
            raise RequiredElementError(
                "Mapper is required: The Mapper for router is not defined")

        super().__init__(*args, **kwargs)

        self.name = default_name
        self.service = service
        self.mapper = mapper

        self.creator_use_case = creator_uc
        self.updater_use_case = updater_uc
        self.deleter_use_case = deleter_uc

        self._include_default_routes()
        self.add_custom_routes()

    def _include_trace_info(self, request: Request,
                            entity: Optional[str] = None, _id: Optional[NomenclatorId] = None,
                            page: Optional[int] = None, count: Optional[int] = None, size: Optional[int] = None):
        """Aggregate the trace_info information"""
        if hasattr(request.state, "trace_info"):
            request.state.trace_info.update(
                {
                    "module": self.__module__,
                    "entity": entity,
                    "identifier": _id,
                    "count": count,
                    "page": page,
                    "size": size
                })

    def _include_default_routes(self):
        """Include or register default nomenclator routes."""

        CreatorType = self.creator_model_class  # pylint: disable=invalid-name
        UpdaterType = self.updater_model_class  # pylint: disable=invalid-name

        @self.post("/status", status_code=status.HTTP_200_OK, tags=[self.name], name=f"Status for API: {self.name} nomenclator")
        async def get_status(request: Request):
            self._include_trace_info(request)
            return JSONResponse(content={"message": "API is running"}, status_code=200)

        @self.post(
            "/", response_model=List[self.response_model_class],
            status_code=status.HTTP_200_OK, tags=[self.name],
            name=f"List of {self.name}'s",
        )
        async def list_items(request: Request,
                             param: Optional[SchemaQueryParam] = Body(
                                 default=None)
                             ) -> List[R]:  # type: ignore
            try:
                elements: List[R] = [
                    self.mapper.map_from_domain_to_schema(domain)
                    for domain in self.service.list_items(
                        pageable=Pageable(
                            page=param.pagination.page,
                            size=param.pagination.element_for_page,
                            pagination=True,
                            sort=param.pagination.sort_mapped()
                        ) if param and param.pagination else None,
                        filters=param.filter.mapped(
                            self.mapper.map_attributes()) if param and param.filter else None,
                    )
                ]

                self._include_trace_info(request,
                                         count=len(elements),
                                         page=param.pagination.page if param and param.pagination else None,
                                         size=self.service.repository_count)

                return elements
            except (ValueError, RequiredElementError, NotImplementedError,
                    RepositoryIntegrityError, RepositoryMissingElementError) as ex:
                raise ForbiddenException(
                    message=f"Error listing items from {self.name} repository.") from ex

        @self.get(
            "/{_id}", response_model=self.response_model_class,
            status_code=status.HTTP_200_OK, tags=[self.name],
            name=f"Get {self.name} item by Id",
        )
        async def get_item_by_id(request: Request, _id: NomenclatorId) -> R:  # type: ignore
            try:
                self._include_trace_info(request, self.service.entity_name)
                domain = self.service.get_item_by_id(_id)
                if not domain:
                    raise NotFoundException(
                        message=f"Item Id: {_id} for {self.name} repository not found")

                return self.mapper.map_from_domain_to_schema(domain)
            except (ValueError, RequiredElementError, NotImplementedError,
                    RepositoryIntegrityError, RepositoryMissingElementError) as ex:
                raise NotFoundException(
                    message=f"Error getting item Id: {_id} from {self.name} repository.") from ex

        @self.delete(
            "/{_id}",
            status_code=status.HTTP_204_NO_CONTENT, tags=[self.name],
            name=f"Delete {self.name} item by Id",
        )
        async def delete_item_by_id(request: Request, _id: NomenclatorId):
            try:
                self._include_trace_info(request)
                self.deleter_use_case.invoke(_id)
            except (RequiredElementError, NotImplementedError, BusinessIntegrityError,
                    RepositoryIntegrityError, RepositoryMissingElementError):
                return Response(status_code=status.HTTP_202_ACCEPTED)

        @self.put(
            "/{_id}", response_model=self.response_model_class,
            status_code=status.HTTP_202_ACCEPTED, tags=[self.name],
            name=f"Update {self.name} item by Id",
        )
        async def update_item_by_id(request: Request, _id: NomenclatorId,
                                    item: UpdaterType = Body(...)) -> R:  # type: ignore

            try:
                self._include_trace_info(request)
                return self.mapper.map_from_domain_to_schema(
                    self.updater_use_case.invoke(
                        self.mapper.map_from_schema_to_domain(
                            item), _id
                    )
                )
            except (ValueError, RequiredElementError, NotImplementedError, BusinessIntegrityError,
                    RepositoryIntegrityError, RepositoryMissingElementError) as ex:
                raise NotFoundException(
                    message=f"Error updating item : {item} from {self.name} repository.") from ex

        @self.post(
            "/create", response_model=self.response_model_class,
            status_code=status.HTTP_201_CREATED, tags=[self.name],
            name=f"Create {self.name} item",
        )
        async def create_item(request: Request,
                              item: CreatorType = Body(...)  # type: ignore
                              ) -> R:  # type: ignore
            try:
                self._include_trace_info(request)
                return self.mapper.map_from_domain_to_schema(
                    self.creator_use_case.invoke(
                        self.mapper.map_from_schema_to_domain(item)
                    )
                )
            except (BusinessIntegrityError, RepositoryIntegrityError) as ex:
                raise ConflictException(
                    f"Error creating item on {self.name} repository.") from ex
            except Exception as ex:
                raise UnprocessableEntityException(
                    f"Error creating item on {self.name} repository.") from ex

    @property
    def response_model_class(self) -> Type[R]:  # type: ignore
        """Get response model class"""
        raise NotImplementedError(
            "The creator model definition must be defined on subclasses")

    @property
    def creator_model_class(self) -> Type[C]:  # type: ignore
        """Get creator model class"""
        raise NotImplementedError(
            "The creator model definition must be defined on subclasses")

    @property
    def updater_model_class(self) -> Type[U]:  # type: ignore
        """Get creator model class"""
        raise NotImplementedError(
            "The creator model definition must be defined on subclasses")

    def add_custom_routes(self):
        """Add custom routes to the router"""


class SimpleNomenclatorRouter(BaseNomenclatorRouter[MapperSchemaSimpleNomenclator]):
    """Simple Nomenclator Router class"""

    @property
    def response_model_class(self) -> Type[SchemaSimpleNomenclatorResponse]:
        """Get response model class"""
        return SchemaSimpleNomenclatorResponse

    @property
    def creator_model_class(self) -> Type[SchemaSimpleNomenclatorCreator]:
        """Get creator model class"""
        return SchemaSimpleNomenclatorCreator

    @property
    def updater_model_class(self) -> Type[SchemaSimpleNomenclatorUpdater]:
        """Get updater model class"""
        return SchemaSimpleNomenclatorUpdater


class NomenclatorRouter(BaseNomenclatorRouter[MapperSchemaNomenclator]):
    """Nomenclator Router class"""

    @property
    def response_model_class(self) -> Type[SchemaNomenclatorResponse]:
        """Get response model class"""
        return SchemaNomenclatorResponse

    @property
    def creator_model_class(self) -> Type[SchemaNomenclatorCreator]:
        """Get creator model class"""
        return SchemaNomenclatorCreator

    @property
    def updater_model_class(self) -> Type[SchemaNomenclatorUpdater]:
        """Get updater model class"""
        return SchemaNomenclatorUpdater
