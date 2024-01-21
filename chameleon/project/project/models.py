from django.db import models

from chameleon.common.django.fields import markup_field
from chameleon.common.django.query import DjangoModelQuery
from chameleon.history.models import ChameleonHistoryBase
from chameleon.history.models import ChameleonObjectWithHistoryBase

__all__ = ["ChameleonProject", "ChameleonProjectHistory"]


class ChameleonProjectHistory(ChameleonHistoryBase):
    objects = models.QuerySet.as_manager()
    query = DjangoModelQuery(objects)


class ChameleonProject(ChameleonObjectWithHistoryBase):
    class Meta:
        ordering = ["creation_time"]

    history_class = ChameleonProjectHistory
    objects = models.QuerySet.as_manager()
    query = DjangoModelQuery(objects)

    title = models.CharField(max_length=200, help_text="Project title")
    description = models.TextField(null=True, help_text="Project description")
    description_markup = markup_field("Project description")

    # ---- creation only -----
    creation_time = models.DateTimeField(help_text="When project has been created")
