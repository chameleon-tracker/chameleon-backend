import datetime
import typing
from collections import abc

from django.db import models

from chameleon.common.django.models import ChameleonBaseModel
from chameleon.history.utils import generate_history_objects
from chameleon.step.mapping.datetime import utcnow

__all__ = ["ChameleonHistoryBase", "ChameleonObjectWithHistoryBase"]


class ChameleonHistoryBase(ChameleonBaseModel):
    class Meta:
        abstract = True

    object_id = models.BigIntegerField()
    timestamp = models.DateTimeField()  # always in UTC TimeZone
    action = models.CharField(max_length=255, help_text="History action")
    field = models.TextField(blank=False, null=True)
    value_from = models.TextField(blank=True, null=True)
    value_to = models.TextField(blank=True, null=True)


class ChameleonObjectWithHistoryBase(ChameleonBaseModel):
    class Meta:
        abstract = True

    history_class: typing.ClassVar[type[ChameleonHistoryBase]]
    creation_type: models.DateTimeField

    async def insert_with_history(self):
        now = utcnow()

        self.creation_time = now  # pylint: disable=attribute-defined-outside-init
        await self.insert()

        source_object = self.to_dict()
        await self.create_history(
            source_object=None,
            target_object=source_object,
            action="CREATE",
            timestamp=now,
        )

    async def update_with_history(self, **values: typing.Any):
        now = utcnow()

        source = self.to_dict()
        self.set_fields(**values)
        await self.update(keys=tuple(values.keys()))
        target = self.to_dict()
        await self.create_history(
            source_object=source, target_object=target, action="UPDATE", timestamp=now
        )

    async def create_history(
        self,
        *,
        source_object: abc.Mapping[str, typing.Any] | typing.Self | None,
        target_object: abc.Mapping[str, typing.Any] | typing.Self | None,
        action: str,
        timestamp: datetime.datetime,
    ):
        history_objects = generate_history_objects(
            source_object=source_object,
            target_object=target_object,
            history_model=self.history_class,
            action=action,
            timestamp=timestamp,
        )
        await self.history_class.query.bulk_create(history_objects)
