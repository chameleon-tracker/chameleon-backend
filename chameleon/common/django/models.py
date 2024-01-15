import typing
from collections import abc
from itertools import chain

from django.db import models

from chameleon.common.query import DjangoModelQuery, AbstractModelQuery


class PrintableModel(models.Model):
    """Generate printable version of a model."""

    class Meta:
        abstract = True

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        """Convert model to a dict."""

        # noinspection PyUnresolvedReferences
        opts = self._meta  # pylint: disable=E1101
        data = {}
        for f in chain(opts.concrete_fields, opts.private_fields):
            data[f.name] = f.value_from_object(self)
        for f in opts.many_to_many:
            data[f.name] = [i.id for i in f.value_from_object(self)]
        return data


class UpdatableModel(models.Model):
    """Add update method from dict to a model."""

    class Meta:
        abstract = True

    def set_fields(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(getattr(self, key), models.Field):
                setattr(self, key, value)
            else:
                raise KeyError(f"Unable to update field {key} as it's not a field")

    async def update(self, keys: abc.Sequence[str] | None = None):
        await self.asave(update_fields=keys, force_update=True)

    async def insert(self):
        await self.asave(force_insert=True)


class ChameleonBaseModel(PrintableModel, UpdatableModel):
    class Meta:
        abstract = True

    objects = models.QuerySet.as_manager()

    query: AbstractModelQuery[models.QuerySet, typing.Self] = DjangoModelQuery(objects)
