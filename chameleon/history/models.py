from django.db import models

from chameleon.common.models import ChameleonBaseModel

__all__ = ["ChameleonHistoryBase"]


class ChameleonHistoryBase(ChameleonBaseModel):
    class Meta:
        abstract = True

    object_id = models.BigIntegerField()
    timestamp = models.DateTimeField()  # always in UTC TimeZone
    action = models.CharField(max_length=255, help_text="History action")
    field = models.TextField(blank=False, null=True)
    value_from = models.TextField(blank=True, null=True)
    value_to = models.TextField(blank=True, null=True)
