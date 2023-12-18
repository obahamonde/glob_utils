"""
Utility functions.
"""
from __future__ import annotations

import asyncio
import functools
from typing import Awaitable, Callable, Generator, Sequence, TypeVar

from typing_extensions import ParamSpec

from ._decorators import robust

T = TypeVar("T")
P = ParamSpec("P")


def chunker(seq: Sequence[T], size: int) -> Generator[Sequence[T], None, None]:
    """
    A generator function that chunks a sequence into smaller sequences of the given size.

    Arguments:
    seq -- The sequence to be chunked.
    size -- The size of the chunks.
    """
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


def async_io(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    """
    Decorator to convert an IO bound function to a coroutine by running it in a thread pool.
    """

    @functools.wraps(func)
    @robust
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper
