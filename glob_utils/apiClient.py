"""
APIClient module, provides an intuitive interface for making HTTP requests.
"""
from typing import Any, AsyncIterable, Dict, List, Literal, Optional, TypeVar, Union

from httpx import AsyncClient
from pydantic import BaseModel  # pylint: disable=E0611

from ._decorators import robust
from ._proxy import LazyProxy

T = TypeVar("T")
Method = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE"]
Json = Union[Dict[str, Any], List[Any], str, int, float, bool, None]
Scalar = Union[str, int, float, bool, None]


class APIClient(BaseModel, LazyProxy[AsyncClient]):
    """
    Generic Lazy Loading APIClient
    Inherits from BaseModel in order to be injected into typed framework such as FastAPI.
    """

    base_url: str
    headers: Dict[str, str]

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.__load__()

    def __load__(self):
        return AsyncClient(base_url=self.base_url, headers=self.headers)

    def dict(self, *args: Any, **kwargs: Any):
        if "exclude" in kwargs:
            kwargs["exclude"].append("headers")
        else:
            kwargs["exclude"] = ["headers"]
        return super().dict(*args, **kwargs)

    @robust
    async def fetch(
        self,
        url: str,
        *,
        method: Method,
        params: Optional[Dict[str, Scalar]] = None,
        json: Optional[Json] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Fetches data from the specified URL using the specified HTTP method.

        Args:
            url (str): The URL to fetch data from.
            method (Method): The HTTP method to use for the request.
            params (Optional[Dict[str, Scalar]], optional): The query parameters to include in the request. Defaults to None.
            json (Optional[Json], optional): The JSON payload to include in the request. Defaults to None.
            headers (Optional[Dict[str, str]], optional): The headers to include in the request. Defaults to None.

        Returns:
            The response object from the request.
        """

        if method in ("GET", "DELETE", "HEAD", "OPTIONS", "TRACE"):
            if headers is not None:
                self.headers.update(headers)
                headers = self.headers
            else:
                headers = self.headers
            response = await self.__load__().request(
                method=method, url=url, headers=headers, params=params
            )
        else:
            if headers is not None:
                self.headers.update(headers)
                headers = self.headers
            else:
                headers = self.headers
            response = await self.__load__().request(
                method=method, url=url, headers=headers, json=json
            )
        return response

    @robust
    async def get(
        self,
        url: str,
        *,
        params: Optional[Dict[str, Scalar]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Sends a GET request to the specified URL.

        Args:
            url (str): The URL to send the GET request to.
            params (Optional[Dict[str, Scalar]], optional): The query parameters to include in the request. Defaults to None.
            headers (Optional[Dict[str, str]], optional): The headers to include in the request. Defaults to None.

        Returns:
            The JSON response from the GET request.
        """
        response = await self.fetch(
            method="GET", url=url, headers=headers, params=params
        )
        return response.json()

    @robust
    async def post(
        self,
        url: str,
        *,
        params: Optional[Dict[str, Scalar]] = None,
        json: Optional[Json] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Sends a POST request to the specified URL with optional parameters, JSON payload, and headers.

        Args:
            url (str): The URL to send the POST request to.
            params (Optional[Dict[str, Scalar]], optional): The query parameters to include in the request URL. Defaults to None.
            json (Optional[Json], optional): The JSON payload to include in the request body. Defaults to None.
            headers (Optional[Dict[str, str]], optional): The headers to include in the request. Defaults to None.

        Returns:
            The JSON response from the server.

        """
        response = await self.fetch(
            method="POST", url=url, json=json, headers=headers, params=params
        )
        return response.json()

    @robust
    async def put(
        self,
        url: str,
        *,
        json: Optional[Json] = None,
        params: Optional[Dict[str, Scalar]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Sends a PUT request to the specified URL with optional JSON payload, query parameters, and headers.

        Args:
            url (str): The URL to send the request to.
            json (Optional[Json], optional): The JSON payload to include in the request body. Defaults to None.
            params (Optional[Dict[str, Scalar]], optional): The query parameters to include in the request URL. Defaults to None.
            headers (Optional[Dict[str, str]], optional): The headers to include in the request. Defaults to None.

        Returns:
            The JSON response from the server.

        """
        response = await self.fetch(
            method="PUT", url=url, json=json, headers=headers, params=params
        )
        return response.json()

    @robust
    async def delete(
        self,
        url: str,
        *,
        params: Optional[Dict[str, Scalar]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        response = await self.fetch(
            method="DELETE", url=url, headers=headers, params=params
        )
        return response.json()

    @robust
    async def patch(
        self,
        url: str,
        *,
        params: Optional[Dict[str, Scalar]] = None,
        json: Optional[Json] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Send a PATCH request to the specified URL.

        Args:
            url (str): The URL to send the PATCH request to.
            params (Optional[Dict[str, Scalar]]): The query parameters to include in the request URL.
            json (Optional[Json]): The JSON payload to include in the request body.
            headers (Optional[Dict[str, str]]): The headers to include in the request.

        Returns:
            The JSON response from the server.

        """
        response = await self.fetch(
            method="PATCH", url=url, json=json, headers=headers, params=params
        )
        return response.json()

    @robust
    async def head(
        self,
        url: str,
        *,
        params: Optional[Dict[str, Scalar]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Sends a HEAD request to the specified URL with optional parameters and headers.

        Args:
            url (str): The URL to send the request to.
            params (Optional[Dict[str, Scalar]], optional): The query parameters to include in the request. Defaults to None.
            headers (Optional[Dict[str, str]], optional): The headers to include in the request. Defaults to None.

        Returns:
            The JSON response from the request.
        """
        response = await self.fetch(
            method="HEAD", url=url, headers=headers, params=params
        )
        return response.json()

    @robust
    async def options(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Send an OPTIONS request to the specified URL.

        Args:
            url (str): The URL to send the request to.
            headers (Optional[Dict[str, str]]): Optional headers to include in the request.

        Returns:
            The JSON response from the server.
        """
        response = await self.fetch(method="OPTIONS", url=url, headers=headers)
        return response.json()

    @robust
    async def trace(
        self,
        url: str,
        *,
        params: Optional[Dict[str, Scalar]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Sends a TRACE request to the specified URL and returns the response as JSON.

        Args:
            url (str): The URL to send the TRACE request to.
            params (Optional[Dict[str, Scalar]]): Optional query parameters to include in the request.
            headers (Optional[Dict[str, str]]): Optional headers to include in the request.

        Returns:
            dict: The response from the server as a JSON object.
        """
        response = await self.fetch(
            method="TRACE", url=url, headers=headers, params=params
        )
        return response.json()

    @robust
    async def text(
        self,
        url: str,
        *,
        method: Method = "GET",
        params: Optional[Dict[str, Scalar]] = None,
        json: Optional[Json] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Sends an HTTP request to the specified URL and returns the response body as text.

        Args:
            url (str): The URL to send the request to.
            method (Method, optional): The HTTP method to use. Defaults to "GET".
            params (Optional[Dict[str, Scalar]], optional): The query parameters to include in the request. Defaults to None.
            json (Optional[Json], optional): The JSON payload to include in the request. Defaults to None.
            headers (Optional[Dict[str, str]], optional): The headers to include in the request. Defaults to None.

        Returns:
            str: The response body as text.
        """
        response = await self.fetch(
            method=method, url=url, json=json, headers=headers, params=params
        )
        return response.text

    @robust
    async def blob(
        self,
        url: str,
        *,
        params: Optional[Dict[str, Scalar]] = None,
        method: Method = "GET",
        json: Optional[Json] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Sends a request to the specified URL and returns the content of the response.

        Args:
            url (str): The URL to send the request to.
            params (Optional[Dict[str, Scalar]], optional): The query parameters to include in the request. Defaults to None.
            method (Method, optional): The HTTP method to use for the request. Defaults to "GET".
            json (Optional[Json], optional): The JSON payload to include in the request. Defaults to None.
            headers (Optional[Dict[str, str]], optional): The headers to include in the request. Defaults to None.

        Returns:
            bytes: The content of the response.
        """
        response = await self.fetch(
            method=method, url=url, json=json, params=params, headers=headers
        )
        return response.content

    async def stream(
        self,
        url: str,
        *,
        method: Method,
        params: Optional[Dict[str, Scalar]] = None,
        json: Optional[Json] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> AsyncIterable[bytes]:
        """
        Sends a streaming request to the specified URL using the specified HTTP method.

        Args:
            url (str): The URL to send the request to.
            method (Method): The HTTP method to use for the request.
            params (Optional[Dict[str, Scalar]]): The query parameters to include in the request URL.
            json (Optional[Json]): The JSON payload to include in the request body.
            headers (Optional[Dict[str, str]]): Additional headers to include in the request.

        Returns:
            AsyncIterable[bytes]: An asynchronous iterable that yields the response data in chunks.
        """
        if headers is not None:
            self.headers.update(headers)
            headers = self.headers
        else:
            headers = self.headers
        response = await self.fetch(
            method=method, url=url, json=json, params=params, headers=headers
        )
        async for chunk in response.aiter_bytes():
            yield chunk
