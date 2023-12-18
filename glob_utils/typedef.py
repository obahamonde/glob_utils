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

class TypeDefinition(TypedDict,total=False):
	name: str
	description: str
	parameters: dict[str, object]

class TypeDefReturn(BaseModel, Generic[R]):
	type: str
	data: R

class TypeDef(BaseModel, Generic[R], ABC):
	@classmethod
	@lru_cache
	def definition(cls) -> TypeDefinition:
		assert cls.__doc__ is not None, "OpenAIFunction must have a docstring"
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
		return TypeDefinition(name=_name, description=_description, parameters=_parameters)

	@cached_property
	def _name(self) -> str:
		return self.__class__.__name__.lower()



	@abstractmethod
	async def run(self) -> R:
		logger.info("Running %s", self.__class__.__name__.lower())
		logger.debug("Parameters: %s", self.json())
		raise NotImplementedError

	@robust
	async def __call__(self) -> TypeDefReturn[R]:
		logger.info("Calling %s", self.__class__.__name__.lower())
		response = await self.run()
		return TypeDefReturn[R](type=self._name, data=response)