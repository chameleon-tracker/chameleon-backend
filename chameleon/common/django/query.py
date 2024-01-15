from collections import abc
import typing

from django.db import models

from chameleon.common.query import AbstractModelQuery


class DjangoModelQuery[ModelType](AbstractModelQuery[models.QuerySet, ModelType]):
    async def first(self):
        return await self.query.aget()

    def __aiter__(self):
        return aiter(self.query.all())

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
