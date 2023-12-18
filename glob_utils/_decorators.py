"""Decorators for robustness, error handling, and timing."""
import asyncio
import functools
import logging
from time import perf_counter
from typing import Awaitable, Callable, Type, TypeVar, Union

from httpx import RequestError
from rich.console import Console
from rich.logging import RichHandler
from rich.pretty import install
from rich.traceback import install as ins
from tenacity import retry as retry_
from tenacity import (retry_if_exception_type, stop_after_attempt,
                      wait_exponential)
from typing_extensions import ParamSpec

from ._exceptions import HTTPException

T = TypeVar("T")
R = TypeVar("R")
P = ParamSpec("P")


def setup_logging(name: str = __name__) -> logging.Logger:
    """
    Set's up logging using the Rich library for pretty and informative terminal logs.

    Arguments:
    name -- Name for the logger instance. It's best practice to use the name of the module where logger is defined.
    """
    install()
    ins()
    console = Console(record=True, force_terminal=True)
    console_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=True,
        markup=True,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        tracebacks_extra_lines=2,
        tracebacks_theme="monokai",
        show_level=False,
    )
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    console_handler.setLevel(logging.INFO)
    logging.basicConfig(level=logging.INFO, handlers=[console_handler])
    logger_ = logging.getLogger(name)
    logger_.setLevel(logging.INFO)
    return logger_


logger = setup_logging()


def process_time(
    func: Callable[P, Union[Awaitable[T], T]]
) -> Callable[P, Awaitable[T]]:
    """
    A decorator to measure the execution time of a coroutine.

    Arguments:
    func -- The coroutine whose execution time is to be measured.
    """

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        """
        Wrapper function to time the function call.
        """
        start = perf_counter()
        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
        end = perf_counter()
        logger.info(
            "Time taken to execute %s: %s seconds", wrapper.__name__, end - start
        )
        return result  # type: ignore

    return wrapper


def handle_errors(
    func: Callable[P, Union[Awaitable[T], T]]
) -> Callable[P, Awaitable[T]]:
    """
    A decorator to handle errors in a coroutine.

    Arguments:
    func -- The coroutine whose errors are to be handled.
    """

    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            wrapper.__name__ = func.__name__
            logger.info("Calling %s", wrapper.__name__)
            if asyncio.iscoroutinefunction(func):
                response = await func(*args, **kwargs)
                logger.info(response)
                return response  # type: ignore
            response = func(*args, **kwargs)
            logger.info(response)
            return response  # type: ignore
        except Exception as exc:
            if isinstance(exc, HTTPException):
                logger.error("%s: %s", exc.status_code, exc.detail) 
                raise exc
            logger.error("%s: %s", exc.__class__.__name__, exc)
            raise exc
    return wrapper


def retry(
    retries: int = 3,
    wait: int = 1,
    max_wait: int = 3,
    exceptions: tuple[Type[Exception], ...] = (RequestError,),
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Wrap an async function with exponential backoff."""

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        @retry_(
            stop=stop_after_attempt(retries),
            wait=wait_exponential(multiplier=wait, max=max_wait),
            retry=retry_if_exception_type(exceptions),
            reraise=True,
        )
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def robust(
    func: Callable[P, Awaitable[T]],
    *,
    max_retries: int = 3,
    wait: int = 1,
    max_wait: int = 3,
    exceptions: tuple[Type[Exception], ...] = (RequestError,)
) -> Callable[P, Awaitable[T]]:
    """
    A decorator to apply error handling, logging and retrying to a coroutine.
    The retrying is configurable with sensible defaults for the following parameters:
    max_retries -- Maximum number of retries. Defaults to 3.
    wait -- Initial wait time in seconds. Defaults to 1.
    max_wait -- Maximum wait time in seconds. Defaults to 3.
    exceptions -- Tuple of exceptions to retry on. Defaults to (RequestError,).
    """
    return functools.reduce(
        lambda f, g: g(f),  # type: ignore
        [retry(max_retries, wait, max_wait, exceptions), process_time, handle_errors],
        func,
    )
