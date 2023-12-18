from typing import Any, AsyncIterator, Dict, List, Literal, Optional, TypeVar, Union

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
    """

    base_url: str
    headers: Dict[str, str]

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.__load__()

    def __load__(self):
        return AsyncClient(base_url=self.base_url, headers=self.headers)

    def dict(self, *args: Any, **kwargs: Any):
        return super().dict(*args, exclude={"headers"}, **kwargs)

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

    async def get(
        self,
        url: str,
        *,
        params: Optional[Dict[str, Scalar]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        response = await self.fetch(
            method="GET", url=url, headers=headers, params=params
        )
        return response.json()

    async def post(
        self,
        url: str,
        *,
        params: Optional[Dict[str, Scalar]] = None,
        json: Optional[Json] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        response = await self.fetch(
            method="POST", url=url, json=json, headers=headers, params=params
        )
        return response.json()

    async def put(
        self,
        url: str,
        *,
        json: Optional[Json] = None,
        params: Optional[Dict[str, Scalar]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        response = await self.fetch(
            method="PUT", url=url, json=json, headers=headers, params=params
        )
        return response.json()

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

    async def patch(
        self,
        url: str,
        *,
        params: Optional[Dict[str, Scalar]] = None,
        json: Optional[Json] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        response = await self.fetch(
            method="PATCH", url=url, json=json, headers=headers, params=params
        )
        return response.json()

    async def head(
        self,
        url: str,
        *,
        params: Optional[Dict[str, Scalar]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        response = await self.fetch(
            method="HEAD", url=url, headers=headers, params=params
        )
        return response.json()

    async def options(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
    ):
        response = await self.fetch(method="OPTIONS", url=url, headers=headers)
        return response.json()

    async def trace(
        self,
        url: str,
        *,
        params: Optional[Dict[str, Scalar]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
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
    ) -> AsyncIterator[bytes]:
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
