import typing
from collections import abc

from django.db import models


class AbstractQuery[QueryType, ModelType]:
    query: QueryType

    def __init__(self, query: QueryType):
        self.query = query

    async def first(self) -> ModelType:
        """Get a single object from query."""
        raise NotImplementedError("Not implemented")

    async def all(self) -> abc.Sequence[ModelType]:
        """Get all objects from query."""
        return [value async for value in self]

    async def __aiter__(self):
        raise NotImplementedError("Not implemented")

    async def bulk_create(self, objects: abc.Sequence[ModelType]):
        raise NotImplementedError("Not implemented")


class AbstractModelQuery[QueryType, ModelType](AbstractQuery[QueryType, ModelType]):
    def by_id(self, pk) -> typing.Self:
        raise NotImplementedError("Not implemented")

    def by_public_id(self, public_id) -> typing.Self:
        raise NotImplementedError("Not implemented")

    def by_project_id(self, project_id) -> typing.Self:
        raise NotImplementedError("Not implemented")

    def by_object_id(self, object_id) -> typing.Self:
        raise NotImplementedError("Not implemented")


class DjangoModelQuery[ModelType](AbstractModelQuery[models.QuerySet, ModelType]):
    async def first(self):
        return await self.query.aget()

    async def __aiter__(self):
        return await self.query.all()

    async def bulk_create(self, objects: abc.Sequence[ModelType]):
        await self.query.abulk_create(objects)

    def by_id(self, pk) -> typing.Self:
        return DjangoModelQuery(self.query.filter(pk=pk))

    def by_public_id(self, public_id) -> typing.Self:
        return DjangoModelQuery(self.query.filter(public_id=public_id))

    def by_project_id(self, project_id) -> typing.Self:
        return DjangoModelQuery(self.query.filter(project_id=project_id))

    def by_object_id(self, object_id) -> typing.Self:
        return DjangoModelQuery(self.query.filter(object_id=object_id))
