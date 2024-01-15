from django.db import models

from chameleon.common.django.fields import markup_field
from chameleon.common.django.models import ChameleonBaseModel
from chameleon.common.django.query import DjangoModelQuery
from chameleon.history.models import ChameleonHistoryBase

__all__ = ["ChameleonProject", "ChameleonProjectHistory"]


class ChameleonProject(ChameleonBaseModel):
    class Meta:
        ordering = ["creation_time"]

    objects = models.QuerySet.as_manager()
    query = DjangoModelQuery(objects)

    title = models.CharField(max_length=200, help_text="Project title")
    description = models.TextField(null=True, help_text="Project description")
    description_markup = markup_field("Project description")

    # ---- creation only -----
    creation_time = models.DateTimeField(help_text="When project has been created")


class ChameleonProjectHistory(ChameleonHistoryBase):
    objects = models.QuerySet.as_manager()
    query = DjangoModelQuery(objects)
