from django.db import models
from itertools import chain


class PrintableModel(models.Model):
    """Generate printable version of a model."""

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        """Convert model to a dict."""

        opts = self._meta
        data = {}
        for f in chain(opts.concrete_fields, opts.private_fields):
            data[f.name] = f.value_from_object(self)
        for f in opts.many_to_many:
            data[f.name] = [i.id for i in f.value_from_object(self)]
        return data

    class Meta:
        abstract = True


class UpdatableModel(models.Model):
    """Add update method from dict to a model."""

    async def update(self, commit: bool = False, /, **kwargs):
        """Update model from a dict.

        Args:
            commit: if automatically commit model
            **kwargs: parameters to update
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        if commit:
            await self.asave(update_fields=kwargs.keys(), force_update=True)

    class Meta:
        abstract = True


class ChameleonBaseModel(PrintableModel, UpdatableModel):
    class Meta:
        abstract = True
