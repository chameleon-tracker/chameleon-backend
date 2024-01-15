from django.db import models

from chameleon.common.django.fields import markup_field
from chameleon.common.django.models import ChameleonBaseModel

from chameleon.history.models import ChameleonHistoryBase

__all__ = ["ChameleonProject", "ChameleonProjectHistory"]


class ChameleonProject(ChameleonBaseModel):
    title = models.CharField(max_length=200, help_text="Project title")
    description = models.TextField(null=True, help_text="Project description")
    description_markup = markup_field("Project description")


class ChameleonProjectHistory(ChameleonHistoryBase):
    ...
