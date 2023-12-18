import asyncio
from typing import AsyncIterable, Generic, TypeVar

from pydantic import BaseModel, Field  # pylint: disable=E0611

T = TypeVar("T", bound=BaseModel)


class Event(BaseModel, Generic[T]):
    event: str = Field(default="message")
    data: T


class EventSource(Generic[T]):
    subscribers: dict[str, asyncio.Queue[Event[T]]] = {}

    async def sub(self, *, key: str) -> AsyncIterable[Event[T]]:
        self._prepare(key=key)
        while True:
            payload = await self.subscribers[key].get()
            yield payload
            if payload.event == "done":
                break

    async def pub(self, *, key: str, event: str, data: T) -> None:
        self._prepare(key=key)
        await self.subscribers[key].put(Event(event=event, data=data))

    def _prepare(self, *, key: str) -> None:
        if key not in self.subscribers:
            self.subscribers[key] = asyncio.Queue()
