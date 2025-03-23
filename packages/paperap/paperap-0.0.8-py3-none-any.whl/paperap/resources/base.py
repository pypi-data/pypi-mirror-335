"""
----------------------------------------------------------------------------

   METADATA:

       File:    base.py
        Project: paperap
       Created: 2025-03-04
        Version: 0.0.8
       Author:  Jess Mann
       Email:   jess@jmann.me
        Copyright (c) 2025 Jess Mann

----------------------------------------------------------------------------

   LAST MODIFIED:

       2025-03-04     By Jess Mann

"""

from __future__ import annotations

import copy
import logging
from abc import ABC, ABCMeta
from string import Template
from typing import TYPE_CHECKING, Any, ClassVar, Final, Generic, Iterator, Optional, cast, overload, override

from pydantic import field_validator
from typing_extensions import TypeVar
from yarl import URL

from paperap.const import URLS, Endpoints
from paperap.exceptions import (
    ConfigurationError,
    ModelValidationError,
    ObjectNotFoundError,
    ResourceNotFoundError,
    ResponseParsingError,
)
from paperap.signals import registry

if TYPE_CHECKING:
    from paperap.client import PaperlessClient
    from paperap.models.abstract import BaseModel, BaseQuerySet, StandardModel, StandardQuerySet

_BaseModel = TypeVar("_BaseModel", bound="BaseModel")
_StandardModel = TypeVar("_StandardModel", bound="StandardModel")
_BaseQuerySet = TypeVar("_BaseQuerySet", bound="BaseQuerySet", default="BaseQuerySet[_BaseModel]", covariant=True)
_StandardQuerySet = TypeVar(
    "_StandardQuerySet", bound="StandardQuerySet", default="StandardQuerySet[_StandardModel]", covariant=True
)

logger = logging.getLogger(__name__)


class BaseResource(ABC, Generic[_BaseModel, _BaseQuerySet]):
    """
    Base class for API resources.

    Args:
        client: The PaperlessClient instance.
        endpoint: The API endpoint for this resource.
        model_class: The model class for this resource.

    """

    # The model class for this resource.
    model_class: type[_BaseModel]
    # The PaperlessClient instance.
    client: "PaperlessClient"
    # The name of the model. This must line up with the API endpoint
    # It will default to the model's name
    name: str
    # The API endpoint for this model.
    # It will default to a standard schema used by the API
    # Setting it will allow you to contact a different schema or even a completely different API.
    # this will usually not need to be overridden
    endpoints: ClassVar[Endpoints]

    def __init__(self, client: "PaperlessClient") -> None:
        self.client = client
        if not hasattr(self, "name"):
            self.name = f"{self._meta.name.lower()}s"

        # Allow templating
        for key, value in self.endpoints.items():
            # endpoints is always dict[str, Template]
            self.endpoints[key] = Template(value.safe_substitute(resource=self.name))  # type: ignore

        # Ensure the model has a link back to this resource
        self._meta.resource = self

        super().__init__()

    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Initialize the subclass.

        Args:
            **kwargs: Arbitrary keyword arguments

        """
        super().__init_subclass__(**kwargs)

        # Skip processing for the base class itself. TODO: This is a hack
        if cls.__name__ in ["BaseResource", "StandardResource"]:
            return

        # model_class is required
        if not (_model_class := getattr(cls, "model_class", None)):
            raise ConfigurationError(f"model_class must be defined in {cls.__name__}")

        # API Endpoint must be defined
        if not (endpoints := getattr(cls, "endpoints", {})):
            endpoints = {
                "list": URLS.list,
                "detail": URLS.detail,
                "create": URLS.create,
                "update": URLS.update,
                "delete": URLS.delete,
            }

        cls.endpoints = cls._validate_endpoints(endpoints)  # type: ignore # Allow assigning in subclass

    @property
    def _meta(self) -> "BaseModel.Meta[_BaseModel]":
        return self.model_class._meta  # pyright: ignore[reportPrivateUsage] # pylint: disable=protected-access

    @classmethod
    def _validate_endpoints(cls, value: Any) -> Endpoints:
        if not isinstance(value, dict):
            raise ModelValidationError("endpoints must be a dictionary")

        converted: dict[str, Template] = {}
        for k, v in value.items():
            if k not in ["list", "detail", "create", "update", "delete"]:
                raise ModelValidationError("endpoint keys must be list, detail, create, update, or delete")

            if isinstance(v, Template):
                converted[k] = v
                continue

            if not isinstance(v, str):
                raise ModelValidationError(f"endpoints[{k}] must be a string or template")

            try:
                converted[k] = Template(v)
            except ValueError as e:
                raise ModelValidationError(f"endpoints[{k}] is not a valid template: {e}") from e

        # list is required
        if "list" not in converted:
            raise ModelValidationError("list endpoint is required")

        # We validated that converted matches endpoints above
        return cast(Endpoints, converted)

    def all(self) -> _BaseQuerySet:
        """
        Return a QuerySet representing all objects of this resource type.

        Returns:
            A QuerySet for this resource

        """
        return self._meta.queryset(self)  # type: ignore # _meta.queryset is always the right queryset type

    def filter(self, **kwargs: Any) -> _BaseQuerySet:
        """
        Return a QuerySet filtered by the given parameters.

        Args:
            **kwargs: Filter parameters

        Returns:
            A filtered QuerySet

        """
        return self.all().filter(**kwargs)

    def get(self, *args: Any, **kwargs: Any) -> _BaseModel:
        """
        Get a model by ID.

        Raises NotImplementedError. Subclasses may implement this.

        Raises:
            NotImplementedError: Unless implemented by a subclass.

        Returns:
            The model retrieved.

        """
        raise NotImplementedError("get method not available for resources without an id")

    def create(self, data: dict[str, Any]) -> _BaseModel:
        """
        Create a new resource.

        Args:
            data: Resource data.

        Returns:
            The created resource.

        """
        # Signal before creating resource
        signal_params = {"resource": self.name, "data": data}
        registry.emit("resource.create:before", "Emitted before creating a resource", kwargs=signal_params)

        if not (template := self.endpoints.get("create")):
            raise ConfigurationError(f"Create endpoint not defined for resource {self.name}")

        url = template.safe_substitute(resource=self.name)
        if not (response := self.client.request("POST", url, data=data)):
            raise ResourceNotFoundError("Resource {resource} not found after create.", resource_name=self.name)

        model = self.parse_to_model(response)

        # Signal after creating resource
        registry.emit(
            "resource.create:after",
            "Emitted after creating a resource",
            args=[self],
            kwargs={"model": model, **signal_params},
        )

        return model

    def update(self, model: _BaseModel) -> _BaseModel:
        """
        Update a resource.

        Args:
            resource: The resource to update.

        Returns:
            The updated resource.

        """
        raise NotImplementedError("update method not available for resources without an id")

    def update_dict(self, model_id: int, **data: dict[str, Any]) -> _BaseModel:
        """
        Update a resource.

        Args:
            model_id: ID of the resource.
            data: Resource data.

        Raises:
            ResourceNotFoundError: If the resource with the given id is not found

        Returns:
            The updated resource.

        """
        # Signal before updating resource
        signal_params = {"resource": self.name, "model_id": model_id, "data": data}
        registry.emit("resource.update:before", "Emitted before updating a resource", kwargs=signal_params)

        if not (template := self.endpoints.get("update")):
            raise ConfigurationError(f"Update endpoint not defined for resource {self.name}")

        url = template.safe_substitute(resource=self.name, pk=model_id)
        if not (response := self.client.request("PUT", url, data=data)):
            raise ResourceNotFoundError("Resource ${resource} not found after update.", resource_name=self.name)

        model = self.parse_to_model(response)

        # Signal after updating resource
        registry.emit(
            "resource.update:after",
            "Emitted after updating a resource",
            args=[self],
            kwargs={**signal_params, "model": model},
        )

        return model

    def delete(self, model_id: int) -> None:
        """
        Delete a resource.

        Args:
            model_id: ID of the resource.

        """
        # Signal before deleting resource
        signal_params = {"resource": self.name, "model_id": model_id}
        registry.emit("resource.delete:before", "Emitted before deleting a resource", args=[self], kwargs=signal_params)

        if not (template := self.endpoints.get("delete")):
            raise ConfigurationError(f"Delete endpoint not defined for resource {self.name}")

        url = template.safe_substitute(resource=self.name, pk=model_id)
        self.client.request("DELETE", url)

        # Signal after deleting resource
        registry.emit("resource.delete:after", "Emitted after deleting a resource", args=[self], kwargs=signal_params)

    def parse_to_model(self, item: dict[str, Any]) -> _BaseModel:
        """
        Parse an item dictionary into a model instance, handling date parsing.

        Args:
            item: The item dictionary.

        Returns:
            The parsed model instance.

        """
        try:
            data = self.transform_data_input(**item)
            return self.model_class.model_validate(data)
        except ValueError as ve:
            logger.error('Error parsing model "%s" with data: %s -> %s', self.name, item, ve)
            raise

    def transform_data_input(self, **data: Any) -> dict[str, Any]:
        """
        Transform data after receiving it from the API.

        Args:
            data: The data to transform.

        Returns:
            The transformed data.

        """
        for key, value in self._meta.field_map.items():
            if key in data:
                data[value] = data.pop(key)
        return data

    @overload
    def transform_data_output(self, model: _BaseModel, exclude_unset: bool = True) -> dict[str, Any]: ...

    @overload
    def transform_data_output(self, **data: Any) -> dict[str, Any]: ...

    def transform_data_output(
        self, model: _BaseModel | None = None, exclude_unset: bool = True, **data: Any
    ) -> dict[str, Any]:
        """
        Transform data before sending it to the API.

        Args:
            model: The model to transform.
            exclude_unset: If model is provided, exclude unset fields when calling to_dict()
            data: The data to transform.

        Returns:
            The transformed data.

        """
        if model:
            if data:
                # Combining model.to_dict() and data is ambiguous, so not allowed.
                raise ValueError("Only one of model or data should be provided")
            data = model.to_dict(exclude_unset=exclude_unset)

        for key, value in self._meta.field_map.items():
            if value in data:
                data[key] = data.pop(value)
        return data

    def create_model(self, **kwargs: Any) -> _BaseModel:
        """
        Create a new model instance.

        Args:
            **kwargs: Model field values

        Returns:
            A new model instance.

        """
        # Mypy output:
        # base.py:326:52: error: Argument "resource" to "BaseModel" has incompatible type
        # "BaseResource[_BaseModel, _BaseQuerySet]"; expected "BaseResource[BaseModel, BaseQuerySet[BaseModel]] | None
        return self.model_class(**kwargs, resource=self)  # type: ignore

    def request_raw(
        self,
        url: str | Template | URL | None = None,
        method: str = "GET",
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """
        Make an HTTP request to the API, and return the raw json response.

        Args:
            method: The HTTP method to use
            url: The full URL to request
            params: Query parameters
            data: Request body data

        Returns:
            The JSON-decoded response from the API

        """
        if not url:
            if not (url := self.endpoints.get("list")):
                raise ConfigurationError(f"List endpoint not defined for resource {self.name}")

        if isinstance(url, Template):
            url = url.safe_substitute(resource=self.name)

        response = self.client.request(method, url, params=params, data=data)
        return response

    def handle_response(self, **response: Any) -> Iterator[_BaseModel]:
        """
        Handle a response from the API and yield results.

        Override in subclasses to implement custom response logic.
        """
        registry.emit(
            "resource._handle_response:before",
            "Emitted before listing resources",
            return_type=dict[str, Any],
            args=[self],
            kwargs={"response": response, "resource": self.name},
        )
        if not (results := response.get("results", response)):
            return

        # Signal after receiving response
        registry.emit(
            "resource._handle_response:after",
            "Emitted after list response, before processing",
            args=[self],
            kwargs={"response": {**response}, "resource": self.name, "results": results},
        )

        yield from self.handle_results(results)

    def handle_results(self, results: list[dict[str, Any]]) -> Iterator[_BaseModel]:
        """
        Yield parsed models from a list of results.

        Override in subclasses to implement custom result handling.
        """
        if not isinstance(results, list):
            raise ResponseParsingError(f"Expected results to be a list, got {type(results)}")

        for item in results:
            if not isinstance(item, dict):
                raise ResponseParsingError(f"Expected type of elements in results is dict, got {type(item)}")

            registry.emit(
                "resource._handle_results:before",
                "Emitted for each item in a list response",
                args=[self],
                kwargs={"resource": self.name, "item": {**item}},
            )
            yield self.parse_to_model(item)

    def __call__(self, *args, **keywords) -> _BaseQuerySet:
        """
        Make the resource callable to get a BaseQuerySet.

        This allows usage like: client.documents(title__contains='invoice')

        Args:
            *args: Unused
            **keywords: Filter parameters

        Returns:
            A filtered QuerySet

        """
        return self.filter(**keywords)


class StandardResource(BaseResource[_StandardModel, _StandardQuerySet], Generic[_StandardModel, _StandardQuerySet]):
    """
    Base class for API resources.

    Args:
        client: The PaperlessClient instance.
        endpoint: The API endpoint for this resource.
        model_class: The model class for this resource.

    """

    # The model class for this resource.
    model_class: type[_StandardModel]

    @override
    def get(self, model_id: int, *args, **kwargs: Any) -> _StandardModel:
        """
        Get a model within this resource by ID.

        Args:
            model_id: ID of the model to retrieve.

        Returns:
            The model retrieved

        """
        # Signal before getting resource
        signal_params = {"resource": self.name, "model_id": model_id}
        registry.emit("resource.get:before", "Emitted before getting a resource", args=[self], kwargs=signal_params)

        if not (template := self.endpoints.get("detail")):
            raise ConfigurationError(f"Get detail endpoint not defined for resource {self.name}")

        # Provide template substitutions for endpoints
        url = template.safe_substitute(resource=self.name, pk=model_id)

        if not (response := self.client.request("GET", url)):
            raise ObjectNotFoundError(resource_name=self.name, model_id=model_id)

        # If the response doesn't have an ID, it's likely a 404
        if not response.get("id"):
            message = response.get("detail") or f"No ID found in {self.name} response"
            raise ObjectNotFoundError(message, resource_name=self.name, model_id=model_id)

        model = self.parse_to_model(response)

        # Signal after getting resource
        registry.emit(
            "resource.get:after",
            "Emitted after getting a single resource by id",
            args=[self],
            kwargs={**signal_params, "model": model},
        )

        return model

    @override
    def update(self, model: _StandardModel) -> _StandardModel:
        """
        Update a model.

        Args:
            model: The model to update.

        Returns:
            The updated model.

        """
        data = model.to_dict()
        data = self.transform_data_output(**data)
        return self.update_dict(model.id, **data)
