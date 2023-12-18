from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterable, Generic, Iterable, Optional, TypeAlias, TypeVar, Union

from pydantic import BaseModel  # pylint: disable=E0611
from typing_extensions import ParamSpec

T = TypeVar("T")
R = TypeVar("R")
I = TypeVar("I", bound=BaseModel)
O = TypeVar("O", bound=BaseModel)
P = ParamSpec("P")

Value: TypeAlias = Union[str, int, float, bool, list[str]]
Query: TypeAlias = Union[
    dict[str, Union[Value, "Query", list["Query"], list[Value]]],
    dict[str, Value],
    dict[str, list["Query"]],
]
Page: TypeAlias = Union[Iterable[T], AsyncIterable[T]]


class QueryBuilder(ABC):
    """
    Query Builder pattern with operation overload for Firebase, DynamoDB and Pinecone.
    """

    @abstractmethod
    def __init__(self, *, field: str, query: Query = {}) -> None:
        raise NotImplementedError

    @abstractmethod
    def __and__(self, other: QueryBuilder) -> QueryBuilder:
        raise NotImplementedError

    @abstractmethod
    def __or__(self, other: QueryBuilder) -> QueryBuilder:
        ...

    @abstractmethod
    def __eq__(self, value: Value) -> QueryBuilder:  # type: ignore
        ...

    @abstractmethod
    def __ne__(self, value: Value) -> QueryBuilder:  # type: ignore
        ...

    @abstractmethod
    def __gt__(self, value: Value) -> QueryBuilder:
        ...

    @abstractmethod
    def __lt__(self, value: Value) -> QueryBuilder:
        ...

    @abstractmethod
    def __ge__(self, value: Value) -> QueryBuilder:
        ...

    @abstractmethod
    def __le__(self, value: Value) -> QueryBuilder:
        ...


class Repository(Generic[I, O], ABC):
    """
    Repository pattern for NoSQL databases
    """

    @abstractmethod
    async def get(self: Repository[I, O], *, key: str, index:Optional[str]) -> Optional[O]:
        raise NotImplementedError

    @abstractmethod
    async def create(self: Repository[I, O], *, key: str, data: I) -> O:
        raise NotImplementedError

    @abstractmethod
    async def update(self: Repository[I, O], *, key: str, data: I) -> O:
        raise NotImplementedError

    @abstractmethod
    async def delete(self: Repository[I,O], *, key: str, index:Optional[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list(self: Repository[I, O],*, limit:Optional[int], offset:Optional[int]) -> Page[O]:
        raise NotImplementedError

    @abstractmethod
    async def query(self: Repository[I, O], *, query: Query) -> Page[O]:
        raise NotImplementedError
