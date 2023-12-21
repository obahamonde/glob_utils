"""Event source module. Abstracts the Pub/Sub pattern."""
import asyncio
from typing import AsyncIterable, Generic, TypeVar

from pydantic import BaseModel, Field  # pylint: disable=E0611

T = TypeVar("T", bound=BaseModel)


class Event(BaseModel, Generic[T]):
    """
    Represents an event with a specific type of data.

    Attributes:
        event (str): The name of the event. Default is "message".
        data (T): The data associated with the event.
    """

    event: str = Field(default="message")
    data: T


class EventSource(Generic[T]):
    """
    Represents a source of events that can be subscribed to and published.

    Attributes:
        subscribers (dict[str, asyncio.Queue[Event[T]]]): A dictionary that maps keys to queues of events.
    """

    subscribers: dict[str, asyncio.Queue[Event[T]]] = {}

    async def sub(self, *, key: str) -> AsyncIterable[Event[T]]:
        """
        Subscribe to events from the specified key.

        Args:
            key (str): The key to subscribe to.

        Yields:
            Event[T]: An event object.

        Raises:
            None

        Returns:
            AsyncIterable[Event[T]]: An asynchronous iterable of events.
        """
        self._prepare(key=key)
        while True:
            payload = await self.subscribers[key].get()
            yield payload
            if payload.event == "done":
                break

    async def pub(self, *, key: str, event: str, data: T) -> None:
        """
        Publish an event to the specified key.

        Args:
            key (str): The key to publish the event to.
            event (str): The event type.
            data (T): The event data.

        Raises:
            None

        Returns:
            None
        """
        self._prepare(key=key)
        await self.subscribers[key].put(Event(event=event, data=data))

    def _prepare(self, *, key: str) -> None:
        """
        Prepare the event source for the specified key.

        Args:
            key (str): The key to prepare.

        Raises:
            None

        Returns:
            None
        """
        if key not in self.subscribers:
            self.subscribers[key] = asyncio.Queue()
