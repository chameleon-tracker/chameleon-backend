import typing
from collections import abc


class AbstractQuery[QueryType, ModelType]:
    """Abstraction layer over a query/session object."""

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

    async def bulk_create(self, objects: abc.Iterable[ModelType]):
        raise NotImplementedError("Not implemented")


class AbstractModelQuery[QueryType, ModelType](AbstractQuery[QueryType, ModelType]):
    """Abstraction layer over query/session object to cover business logic."""

    def by_id(self, pk) -> typing.Self:
        raise NotImplementedError("Not implemented")

    def by_public_id(self, public_id) -> typing.Self:
        raise NotImplementedError("Not implemented")

    def by_project_id(self, project_id) -> typing.Self:
        raise NotImplementedError("Not implemented")

    def by_object_id(self, object_id) -> typing.Self:
        raise NotImplementedError("Not implemented")

    def by_ticket_id(self, ticket_id) -> typing.Self:
        raise NotImplementedError("Not implemented")
