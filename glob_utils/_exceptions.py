"""
Exceptions Handling
"""
from __future__ import annotations

from functools import singledispatch

from fastapi import HTTPException
from httpx import RequestError
from pydantic import ValidationError
from typing_extensions import Generic, Type, TypeVar

E = TypeVar("E", bound=Exception, contravariant=True)

EXCEPTIONS: dict[str, int] = {
    "ConnectError": 503,
    "ConnectTimeout": 408,
    "DecodingError": 422,
    "HTTPError": 500,
    "LocalProtocolError": 500,
    "NetworkError": 503,
    "PoolTimeout": 503,
    "ProtocolError": 500,
    "ProxyError": 502,
    "ReadTimeout": 408,
    "RemoteProtocolError": 502,
    "StreamError": 500,
    "TimeoutException": 408,
    "TooManyRedirects": 310,
    "TransportError": 503,
    "UnsupportedProtocol": 505,
    "WriteTimeout": 408,
    "TimeoutError": 408,
    "ConnectionError": 503,
    "ConnectionRefusedError": 503,
    "ConnectionResetError": 503,
    "asyncio.TimeoutError": 408,
    "UnicodeDecodeError": 400,
    "UnicodeEncodeError": 400,
    "UnicodeError": 400,
    "TypeError": 400,
    "ValueError": 400,
    "ZeroDivisionError": 500,
    "IndexError": 400,
    "AttributeError": 500,
    "ImportError": 500,
    "ModuleNotFoundError": 500,
    "NotImplementedError": 501,
    "RecursionError": 500,
    "OverflowError": 500,
    "KeyError": 404,
    "Exception": 500,
    "HTTPException": 500,
}


class APIException(HTTPException, Generic[E]):
    """
    API Exception
    """

    def __init__(
        self, status_code: int = 500, message: str = "Internal Server Error"
    ) -> None:
        """
        API Exception

        Arguments:
                                    - status_code: HTTP status code
                                    - message: Message to be displayed
        """
        super().__init__(status_code=status_code, detail=message)


@singledispatch
def handle_exception(exc: Type[E]) -> APIException[E]:
    """
    Handle exceptions and return a HttpException

    Arguments:
                                    - exc: Exception to be handled

    Returns:
                                    - HttpException
    """
    raise NotImplementedError()


@handle_exception.register(ValidationError)
def _(exc: ValidationError) -> APIException[ValidationError]:
    raise HTTPException(status_code=400, detail=exc.json())


@handle_exception.register(RequestError)
def _(exc: RequestError) -> APIException[RequestError]:
    request_info = f"{exc.__class__.__name__}: {exc.request.method} {exc.request.url}"
    raise HTTPException(status_code=EXCEPTIONS[exc.__class__.__name__], detail=request_info)


@handle_exception.register(Exception)
def _(exc: Exception) -> APIException[Exception]:
    if exc.__class__.__name__ in EXCEPTIONS:
        raise HTTPException(
            status_code=EXCEPTIONS[exc.__class__.__name__], detail=str(exc)
        )
    raise HTTPException(status_code=500, detail=str(exc))