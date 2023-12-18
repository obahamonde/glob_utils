from typing import Any, Generic, Optional, TypeVar

from fastapi import APIRouter
from pydantic import BaseModel  # pylint: disable=E0611

from .repository import Page, Query, Repository

I = TypeVar("I", bound=BaseModel)
O = TypeVar("O", bound=BaseModel)

class Controller(APIRouter, Generic[I,O]):
	repository: Repository[I,O]
	
	def __init__(self, *args:Any, repository: Repository[I,O], **kwargs: Any):
		super().__init__(*args, **kwargs)
		self.repository = repository
		self.add_api_route(path="/", methods=["GET"], endpoint=self._list)
		self.add_api_route(path="/", methods=["POST"], endpoint=self._create)
		self.add_api_route(path="/{key}", methods=["GET"], endpoint=self._get)
		self.add_api_route(path="/{key}", methods=["PUT"], endpoint=self._update)
		self.add_api_route(path="/{key}", methods=["DELETE"], endpoint=self._delete)
		self.add_api_route(path="/query", methods=["POST"], endpoint=self._query)
		
	async def _list(self, *, limit:Optional[int], offset:Optional[int]) -> Page[O]:
		return await self.repository.list(limit=limit, offset=offset)
	
	async def _get(self, *, key: str, index:Optional[str]) -> Optional[O]:
		return await self.repository.get(key=key, index=index)
	
	async def _create(self, *, key:str,item: I) -> O:
		return await self.repository.create(key=key,data=item)
	
	async def _update(self, *, key:str,item: I) -> O:
		return await self.repository.update(key=key,data=item)
	
	async def _delete(self, *, key:str,index:Optional[str]) -> None:
		return await self.repository.delete(key=key,index=index)
	
	async def _query(self, *, query: Query) -> Page[O]:
		return await self.repository.query(query=query)