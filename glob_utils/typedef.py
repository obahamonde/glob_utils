"""This module provides a base class for defining types with a well-defined schema and well-documented parameters."""
import base64
import json
from abc import ABC, abstractmethod
from functools import cached_property, lru_cache, singledispatch
from typing import Any, Generic, TypedDict, TypeVar, cast

from pydantic import BaseModel  # pylint: disable=E0611

from ._decorators import robust, setup_logging

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R")

logger = setup_logging()


@singledispatch
def parse_output(output: Any) -> str:
    """
    Parses an output from a TypeDef run method into a string.

    Arguments:
    output -- The output to be parsed.
    """
    return str(output)


@parse_output.register
def _(output: BaseModel) -> str:
    return output.json()


@parse_output.register
def _(output: bytes) -> str:
    return base64.b64encode(output).decode("utf-8")


@parse_output.register
def _(output: dict) -> str:  # type: ignore
    return json.dumps({k: parse_output(v) for k, v in output.items()})  # type: ignore


@parse_output.register
def _(output: list) -> str:  # type: ignore
    return json.dumps([parse_output(item) for item in output])  # type: ignore


class TypeDefinition(TypedDict, total=False):
    """
    Represents a `json-schema` definition for a type.
    Attributes:
                        name (str): The name of the type.
                        description (str): A description of the type.
                        parameters (dict[str, object]): The parameters of the type.
    """

    name: str
    description: str
    parameters: dict[str, object]


class TypeDefReturn(BaseModel, Generic[R]):
    """
    Represents a return type definition.

    Attributes:
            type (str): The type of the return value.
            data (R): The actual return value.
    """

    type: str
    data: R


class TypeDef(BaseModel, Generic[R], ABC):
    """
    Represents a type definition.

    This class provides a base implementation for defining types with a well-defined schema and well-documented parameters.

    It also provides a base for implementing a `run` method that returns a value of type `R`that is parsed into a `TypeDefReturn` object indicating the type of the return value in the `type` attribute and the actual return value in the `data` attribute in order to be able to parse the return value into a string.
    """

    @classmethod
    @lru_cache
    def definition(cls) -> TypeDefinition:
        """
        Returns a `TypeDefinition` object representing the type definition.

        The `TypeDefinition` object is cached to avoid recomputing it every time it is called.
        """
        assert cls.__doc__ is not None, "TypeDefinitions must have a docstring"
        _schema = cls.schema()  # type: ignore
        _name = cls.__name__.lower()
        _description = cls.__doc__
        _parameters = cast(
            dict[str, object],
            (
                {
                    "type": "object",
                    "properties": {
                        k: v for k, v in _schema["properties"].items() if k != "self"
                    },
                    "required": _schema.get("required", []),
                }
            ),
        )
        return TypeDefinition(
            name=_name, description=_description, parameters=_parameters
        )

    @cached_property
    def _name(self) -> str:
        return self.__class__.__name__.lower()

    @abstractmethod
    async def run(self) -> R:
        """
        Runs the type definition and returns the result. The implementation of this method is up to the user.
        """
        ...

    @robust
    async def __call__(self) -> TypeDefReturn[R]:
        logger.info("Calling %s", self._name)
        response = await self.run()
        return TypeDefReturn[R](type=self._name, data=response)
